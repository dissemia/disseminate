"""
Classes and functions for rendering documents.
"""
from tempfile import mkdtemp
from shutil import rmtree
from collections import OrderedDict
import weakref
import logging
import os
import os.path

from ..ast import (process_ast, process_paragraphs, process_typography,
                   process_context_tags)
from ..templates import get_template
from ..header import load_yaml_header
from ..tags import Tag
from ..macros import replace_macros
from ..convert import convert
from ..labels import LabelManager
from ..dependency_manager import DependencyManager
from ..utils import mkdir_p
from .. import settings


class DocumentError(Exception):
    """An error generated while loading and processing a document."""
    pass


class Document(object):
    """A base class document rendered from a source file to a target file.

    Parameters
    ----------
    src_filepath : str
        The path (relative to the current directory) for the document (markup
        source) file of this document.
    target_root : str, optional
        The path for the rendered target files. To this directly, the target
        extension subdirectories (ex: 'html' 'tex') will be created.
        By default, if not specified, the target_root will be one directory
        above the project_root.
    context : dict, optional
        The context of the document.

    Attributes
    ----------
    src_filepath : str
        The filename and path for this document's (markup source) file. This
        file should exist. This path is a render path: it's either an absolute
        path or a path relative to the current directory.
        ex: 'src/chapter1/chapter1.dm'
    context : dict
        The context with values for the document.
    subdocuments : :collections:`OrderedDict`
        An ordered dict with the sub-documents included in this document.
        The keys are src_filepath values as render paths, and the values
        are the subdocuments themselves. The documents are ordered according
        to their placement in the document tree.

        This document owns the subdocuments and only weak references to these
        documents should be made. (i.e. when the subdocuments dict is cleared,
        the memory for the document objects should be released)

    string_processors : list of functions, **class attribute**
        A list of functions to process the string before conversion to the
        AST. These functions are executed in sequence and simply accept the
        string, local_context and global_context as arguments and return a
        processed string. The processed string can either be a 'str' or a
        'Metastring' with additional meta information.

        .. note:: String processors are run asynchronously, and the
                  local_context and global_context dicts may not be fully
                  populated.

    ast_processors : list of functions, **class attribute**
        A list of functions to process the AST. These functions are executed in
        sequence and simply accept a AST argument and return a processed AST.

        .. note:: AST processors are run asynchronously, and the
                  local_context and global_context dicts may not be fully
                  populated.

    context_processors : list of functions, **class attribute**
        A list of functions to process the document's context while the target
        is being rendered. The context_processor functions take a context and a
        target as parameters.
    """

    src_filepath = None
    context = None
    subdocuments = None

    #: The context dict for the document that owns this document. For the root
    #: document, this attribute is None
    _parent_context = None

    #: The calculated target_root, based on the value specified or a value
    #: evaluated from the project_root
    _target_root = None

    #: The path of a temporary directory created for this document, if needed.
    _temp_dir = None

    #: Cached template objects for this document.
    _templates = None

    #: String processors, before loading the AST.
    #: def string_processor(s, context)
    string_processors = [load_yaml_header,  # Process YAML headers
                         replace_macros,  # Process macros
                         ]

    #: Abstract Syntax Tree (AST) processors.
    #: def ast_processor(ast, context, src_filepath)
    ast_processors = [process_ast,
                      process_paragraphs,
                      process_typography,
                      process_context_tags,
                      ]

    #: Context processors
    context_processors = []

    def __init__(self, src_filepath, target_root=None, context=None):
        self.src_filepath = str(src_filepath)
        self.subdocuments = OrderedDict()
        self.context = dict(settings.default_context)  # create a copy
        self._templates = dict()

        self._parent_context = context
        src_path = os.path.split(self.src_filepath)[0]

        # Set the src_filepaths of the document and sub-documents
        self._subdocuments_src_filepaths = []

        # Set the target_root.
        # Otherwise use the directory above the src_path
        if target_root is not None:
            # Use the specified value, if available.
            self._target_root = target_root
        elif isinstance(context, dict) and 'target_root' in context:
            self._target_root = context['target_root']
        elif src_path.endswith(settings.document_src_directory):
            # If the src_path is in a src_directory, use the directory above
            # this directory
            self._target_root = os.path.split(src_path)[0]
        else:
            # Otherwise just use the same directory as the src directory
            self._target_root = src_path

        # Reset the context
        self.reset_contexts()

        # The cached AST
        self._ast = None

        # Read in the AST and load subdocuments
        self.get_ast()

    def __del__(self):
        """Clean up any temp directories no longer in use."""
        if self._temp_dir is not None:
            rmtree(self._temp_dir, ignore_errors=True)

        # Reset the labels for this document
        label_manager = self.context.get('label_manager', None)
        if label_manager is not None:
            label_manager.reset(document=self)

        # Reset the dependencies for this document
        self.reset_dependencies()

    def __repr__(self):
        return "Document({})".format(self.src_filepath)

    @property
    def title(self):
        """The title for the document."""
        if 'title' in self.context:
            # The title entry could be a string or a tag. If it's a tag, just
            # get the text for the tag.
            title = self.context['title']
            title_str = (title.default_fmt().strip()
                         if hasattr(title, 'default_fmt')
                         else title)
            return title_str
        return self.src_filepath.strip(settings.document_extension)

    @property
    def short(self):
        """The short title for the document."""
        if 'short' in self.context:
            # The short entry could be a string or a tag. If it's a tag, just
            # get the text for the tag.
            short = self.context['short']
            short_str = (short.default_fmt().strip()
                         if hasattr(short, 'default_fmt')
                         else short)
            return short_str
        else:
            return self.title

    @property
    def number(self):
        """The number of the document.

        Returns
        -------
        number : int or None
            The number (order) of the document in relation to all documents in
            a project or,
            None, if the document's number hasn't yet been assigned.
        """
        root_document = self.context.get('root_document', None)
        root_document = root_document() if root_document is not None else None

        # Get all documents from the root document
        if root_document is not None:
            all_docs = root_document.documents_list(only_subdocuments=False,
                                                    recursive=True)
            return all_docs.index(self) + 1 if self in all_docs else None
        else:
            return None

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = mkdtemp()
        return self._temp_dir

    @property
    def mtime(self):
        return self.context.get('mtime', None)

    @property
    def project_root(self):
        if 'project_root' in self.context:
            return self.context['project_root']
        else:
            return os.path.split(self.src_filepath)[0]

    @property
    def target_root(self):
        if 'target_root' in self.context:
            return self.context['target_root']
        else:
            return self._target_root

    @property
    def target_list(self):
        """The list of targets from the context."""
        # Refresh the context
        self.get_ast()

        # Get the targets from the context
        targets = self.context.get('targets', settings.document_target_list)

        # Convert to a list, if needed
        target_list = (targets.split(',') if isinstance(targets, str) else
                       targets)

        if len(target_list) == 1:
            target_list = [t.strip() for t in target_list[0].split(" ")]
        else:
            target_list = [t.strip() for t in target_list]

        if 'none' in target_list:
            return []

        # Add trailing period to extensions in target_list
        return [t if t.startswith('.') else '.' + t for t in target_list]

    @property
    def targets(self):
        """The targets dict.

        Returns
        -------
        targets : dict
            The targets are a dict with the target extension as keys
            (ex: '.html') and the value is the target_filepath for that target.
            (ex: 'html/index.html') These paths are render paths: they're
            either an absolute path or a path relative to the current
            directory.
        """
        target_list = self.target_list

        # Keep a list of extensions without the trailing period
        # ex: ['html', 'pdf']
        stripped_exts = [ext[1:] for ext in target_list]

        # Create the target dict
        targets = dict()
        base_target = self.target_root

        # Get the filename relative to the project root
        project_filename = os.path.relpath(self.src_filepath, self.project_root)

        # Strip the extension
        project_basefilename = os.path.splitext(project_filename)[0]

        for target_ext, stripped_ext in zip(target_list, stripped_exts):
            t = (os.path.join(str(base_target), str(stripped_ext),
                              str(project_basefilename)) +
                 target_ext)
            targets[target_ext] = t
        return targets

    def target_filepath(self, target, render_path=True):
        """The filepath for the given target extension.

        Parameters
        ----------
        target : str
            The target extension for the target file.
            ex: '.html' or '.tex'
        render_path : bool
            If True, the returned target_filepath is a render path---i.e. it
            is an absolute path or relative to the current directory.
            If False, the returned target_filepath is relative to the target
            root, including the target subdirectory.
        """
        assert target in self.targets

        if not render_path:
            # Get the target_root. The actual target path includes the target
            # extension as a subdirectory.
            target_root = os.path.join(self.target_root, target.strip('.'))
            return os.path.relpath(self.targets[target], target_root)

        return self.targets[target]

    def reset_contexts(self):
        """Clear and repopulate the local_context and global_context.

        The context contains one of the following for all documents in a root
        document:
          1. label_manager: Manages labels and references to labels.
          2. dependency_manager: Manages the media dependencies (like image
             files) for documents
          3. project_root: the root directory (render path) for the document
             and sub-documents
          4. target_root: the root directory (render path) for the document
             and sub-documents. The final target path includes a sub-directory
             for the target's extension.
          5. root_document: an :obj:`disseminate.Document` root document for
             the project.

        Context variables that can be local to a document are:
          1. targets: a listing of target formats to render to.
          2. include: the sub-documents to include under a document.
          3. title: the title of a document.
          4. short: the short title of a document.
          5. toc: the kind of table-of-contents to render for a document.
          6. template: the template file to use in rendering a document.
          7. render: the specific render mode.
             - single: render only the given document (default)
             - collection: include all sub-documents in the render--i.e. for
               a book.
          9. document: a weakref to this document.
          10. mtime: The modification time of the source document. This is
              populated by the get_ast method.
        """
        # Remove everything from the context dict except for objects that
        # need to be preserved between documents, like the label_manager and
        # dependency_manager
        excluded_items = ('label_manager', 'dependency_manager',
                          'project_root', 'target_root', 'root_document')
        context_keys = list(self.context.keys())
        for k in context_keys:
            if k in excluded_items:
                continue
            del self.context[k]

        # Copy over the context values from parent context. The excluded_items
        # do not pertain to sub-documents.
        excluded_items = ('include', 'title', 'short', 'render', 'mtime')
        if self._parent_context is not None:
            for k, v in self._parent_context.items():
                if k in excluded_items:
                    continue
                self.context[k] = v

        self.context['document'] = weakref.ref(self)

        # The following tests whether the context values came from a parent
        # document
        if self.context.get('src_filepath', None) != self.src_filepath:
            # Set the document's level. The root document is level 1, its'
            # sub-documents are level 2, their sub-documents are level 3
            self.context['level'] = self.context.get('level', 0) + 1

        self.context['src_filepath'] = self.src_filepath

        # The following should only be set by the root target document
        if 'project_root' not in self.context:
            self.context['project_root'] = self.project_root
        if 'target_root' not in self.context:
            self.context['target_root'] = self.target_root
        if 'label_manager' not in self.context:
            self.context['label_manager'] = LabelManager()
        if 'dependency_manager' not in self.context:
            dep = DependencyManager(project_root=self.project_root,
                                    target_root=self.target_root)
            self.context['dependency_manager'] = dep
        if 'root_document' not in self.context:
            self.context['root_document'] = weakref.ref(self)

    def reset_dependencies(self):
        """Clear and repopulate the dependencies for this document in the
        dependency manager."""
        if 'dependency_manager' in self.context:
            document_src_filepath = self.src_filepath
            dep = self.context['dependency_manager']
            dep.reset(document_src_filepath=document_src_filepath)

    def reset_labels(self):
        """Reset the labels for this document in the label manager.

        .. note:: This function is invoked as part of the get_ast method, after
                  parsing the source file, so that the 'title' attribute can be
                  retrieved from the local_context.
        """
        if 'label_manager' in self.context:
            label_manager = self.context['label_manager']

            # Reset the labels for this document
            label_manager.reset(document=self)

            project_filepath = os.path.relpath(self.src_filepath,
                                               self.project_root)

            # Get the level of the document
            level = self.context.get('level', 1)

            # Set the label for this document
            kind = ('document', 'document-level-' + str(level))
            label_manager.add_label(document=self, kind=kind,
                                    id='doc:' + project_filepath)

    def documents_dict(self, document=None, only_subdocuments=False,
                       recursive=False):
        """Produce an ordered dict of a document and all its sub-documents.

        Parameters
        ----------
        document : :obj:`disseminate.Document`, optional
            The document for which to create the document list.
            If None is specified, this document will be used.
        only_subdocuments : bool, optional
            If True, only the sub-documents will be returned (not this
            document or the document specified.)
        recursive : bool, optional
            If True, the sub-documents of sub-documents are returned (in order)
            in the ordered dict as well

        Returns
        -------
        document_dict : ordered dict of :obj:`disseminate.Document`
            An ordered dict of documents.
            The keys are src_filepath strings (render paths) and the values
            are document objects.
        """
        document = self if document is None else document
        doc_dict = OrderedDict()

        if not only_subdocuments:
            doc_dict[document.src_filepath] = document

        for src_filepath, subdoc in document.subdocuments.items():

            if recursive:
                subdoc_dict = subdoc.documents_dict(only_subdocuments=False,
                                                    recursive=recursive)
                for k,v in subdoc_dict.items():
                    doc_dict[k] = v
            else:
                doc_dict[subdoc.src_filepath] = subdoc

        return doc_dict

    def documents_list(self, document=None, only_subdocuments=False,
                       recursive=False):
        """Produce an ordered list of a document and all its sub-documents.

        Parameters
        ----------
        document : :obj:`disseminate.Document`, optional
            The document for which to create the document list.
        only_subdocuments : bool, optional
            If True, only the sub-documents will be returned (not this root
            document or the document specified.
        recursive : bool, optional
            If True, the sub-documents of sub-documents are returned (in order)
            in the list as well

        Returns
        -------
        document_list : list of :obj:`disseminate.Document`
            An ordered list of documents.
        """
        doc_dict = self.documents_dict(document=document,
                                       only_subdocuments=only_subdocuments,
                                       recursive=recursive)

        return list(doc_dict.values())

    def load_subdocuments(self):
        """Load the sub-documents listed in the include of a local_context."""

        # Get the root document's src_filepath and the src_filepath for all of
        # its included subdocuments to make sure we do not load documents
        # recursively or twice
        root_document = self.context.get('root_document', None)
        root_document = root_document() if root_document is not None else None

        # Get the documents dict for the root document, including all
        # subdocuments
        root_dict = root_document.documents_dict(document=root_document,
                                                 only_subdocuments=False,
                                                 recursive=True)

        # Clear the subdocuments ordered dict and add new entries. Old entries
        # will automatically be delete if the subdocument no longer holds a
        # reference to it.
        self.subdocuments.clear()

        if 'include' in self.context:
            # Get the included subdocument paths
            src_filepaths = self.context['include']
            if isinstance(src_filepaths, str):
                src_filepaths = src_filepaths.split()
            src_filepaths = [s for s in src_filepaths if isinstance(s, str)]

            # Move the document to this document's subdocuments ordered
            # directory, if the document already exists, or create a new
            # document for missing documents.
            current_src_path = os.path.split(self.src_filepath)[0]

            for src_filepath in src_filepaths:
                # Add the current path to make it a render_path
                render_filepath = os.path.join(current_src_path, src_filepath)

                # If the document is already loaded, copy it to the subdocuments
                # ordered dict
                if render_filepath in root_dict:
                    subdoc = root_dict[render_filepath]

                    if self.src_filepath not in subdoc.subdocuments:
                        self.subdocuments[render_filepath] = subdoc
                    continue

                # The document could not be found, at this point. Create it.
                logging.debug("Creating document: {}".format(render_filepath))

                # Create the document and add it to the subdocuments ordered
                # dict.
                subdoc = Document(src_filepath=render_filepath,
                                  context=self.context)
                self.subdocuments[render_filepath] = subdoc

    def get_template(self, target, reload=False):
        """Get the template for this document.

        Parameters
        ----------
        target : str
            The target for the template. ex: '.html'
        reload : bool, optional
            By default, this method returns cached template objects. If this
            flag is set to True, then the template object will be reloaded and
            returned. This needs to be done if the template object needs to be
            updated.

        Returns
        -------
        template
        """
        template_basename = settings.template_basename
        if 'template' in self.context:
            template_basename = self.context['template']

        # Generate a cached template, if needed. Using the same template object
        # between renders is needed so that the 'is_up_to_date' attribute
        # is properly updated if the template file is re-written
        if template_basename not in self._templates or reload:
            template = get_template(self.src_filepath, target=target,
                                    template_basename=template_basename)
            self._templates[template_basename] = template

        return self._templates[template_basename]

    def get_ast(self, reload=False):
        """Process and return the AST.

        This method generates and caches the AST. This step is conducted
        asynchronously. (i.e. the local_context and global_context may not be
        completed populated while the AST is processed.)

        The cached AST is updated if the source file is updated.

        Whenever the AST is generated, the local_context is reset to avoid
        keeping stale values.

        See the :meth:`render` method for more details.

        Parameters
        ----------
        reload : bool, optional
            If True, force the reload of the AST.

        Returns
        -------
        :obj:`disseminate.tag.Tag`
            A root tag object for the AST.
        """
        # Check to make sure the file exists
        if not os.path.isfile(self.src_filepath):  # file must exist
            msg = "The source document '{}' must exist."
            raise DocumentError(msg.format(self.src_filepath))

        stat = os.stat(self.src_filepath)
        time = stat.st_mtime

        last_mtime = self.mtime

        # Update the AST, if needed
        if (getattr(self, '_ast', None) is None or
           last_mtime is None or time > last_mtime or
           reload):

            # Check to make sure the file is reasonable
            filesize = stat.st_size
            if filesize > settings.document_max_size:
                msg = ("The source document '{}' has a file size ({} kB) "
                       "that exceeds the maximum setting size of {} kB.")
                raise DocumentError(msg.format(self.src_filepath,
                                            filesize / 1024,
                                            settings.document_max_size / 1024))

            # Load the string from the src_filepath,
            with open(self.src_filepath) as f:
                string = f.read()

            # Reset the local_context. When reloading an AST, the old
            # local_context is invalidated since some of the entries may have
            # changed
            self.reset_contexts()

            # Clear the dependencies for this document
            self.reset_dependencies()

            # Reset the registered labels for this document and set the
            # document's label
            self.reset_labels()

            # Process the string
            for processor in self.string_processors:
                string = processor(string, self.context)

            # Process and validate the AST
            ast = string
            for processor in self.ast_processors:
                ast = processor(ast=ast, context=self.context,
                                src_filepath=self.src_filepath)

            # Load the sub-documents. This is done after processing the string
            # and ast since these may include sub-files, which should be read
            # in before being loaded.
            self.load_subdocuments()

            # cache the ast
            self._ast = ast
            self.context['mtime'] = time

        # Run get_ast for the sub-documents. This should be done after loading
        # this document's AST since this document's header may have includes
        for document in self.documents_list(only_subdocuments=True):
            document.get_ast(reload=reload)

        # Return this document's AST
        return self._ast

    def get_grouped_asts(self, target, reload=False):
        """Group the ASTs for the given document and sub-documents for the given
        target.

        Parameters
        ----------
        target : str
            Only include ASTs for the document and sub-documents that have this
            target in their target_list.
        reload : bool, str
            If True, force the reload of the AST.

        Returns
        -------
        ast : list or :obj:`disseminate.tag.Tag`
            A root tag object for the AST.
         """
        asts = []

        # Load the ASTs for all documents
        self.get_ast()

        # Get a listing of all documents (recursively and including the root
        # document) in order.
        documents = self.documents_list(only_subdocuments=False, recursive=True)

        # Remove documents that don't have the target listed in their
        # target_list
        documents = [d for d in documents if target in d.target_list]

        # Group the ASTs
        for doc in documents:
            ast = doc.get_ast()

            # Unwrap the root tag, if present
            if isinstance(ast, Tag) and ast.name == 'root':
                ast = ast.content

            if isinstance(ast, list):
                asts += ast
            else:
                asts.append(ast)

        # Wrap the ast in a root tag
        root = Tag(name='root', content=asts, attributes=None,
                   context=self.context)
        return root

    def render_required(self, target_filepath):
        """Evaluate whether a render is required to write the target file.

        Parameters
        ----------
        target_filepath : The render path for the target file.

        Returns
        -------
        render_required : bool
            True, if a render is required.
            False if a render isn't required.
        """
        render_mode = self.context.get('render', 'single')
        target = os.path.splitext(target_filepath)[1]

        # 1. A render is required if the target_filepath doesn't exist
        if not os.path.isfile(target_filepath):
            logging.debug("Render required for {}: '{}' target file "
                          "does not exist.".format(self, target_filepath))
            return True

        # Get the modification time for the source file(s) (src_filepath)
        if render_mode == 'collection':
            # Get the latest modification time for the included source files
            mtimes = map(lambda x: os.path.getmtime(x.src_filepath),
                         self.documents_list())
            src_mtime = max(mtimes)
        else:
            src_mtime = os.path.getmtime(self.src_filepath)

        # Get the modification for the target file (target_filepath)
        target_mtime = os.path.getmtime(target_filepath)

        # 2. A render is required if the src_filepath mtime is newer than the
        # target_filepath
        if src_mtime > target_mtime:
            logging.debug("Render required for {}: '{}' target file "
                          "is older than source.".format(self, target_filepath))
            return True

        # 3. A render is required if the tags or labels used by this document
        #    have been updated since the target file was written. This is
        #    because the label numbers and contents for *other* documents may
        #    have changed.
        tag_mtime = (self._ast.mtime if hasattr(self, '_ast') and
                                        hasattr(self._ast, 'mtime') else None)
        if tag_mtime is not None and target_mtime < tag_mtime:
            logging.debug("Render required for {}:  The tags reference a "
                          "document that's been updated.".format(self))
            return True

        # 4. A render is required if the template is not up to date. Simply
        #    calling the 'get_template' method will return the current template
        #    object, which can be used to test whether it's up to date. In the
        #    render_uncompiled method, the template is reloaded to guarantee
        #    that the latest template is loaded.
        template = self.get_template(target=target)
        if not template.is_up_to_date:
            logging.debug("Render required for {}:  The template has been "
                          "updated.".format(self))
            return True

        # All tests passed. No new render is needed
        return False

    def render(self, targets=None, create_dirs=settings.create_dirs,
               update_only=True, subdocuments=True):
        """Render the document to one or more target formats.

        Parameters
        ----------
        targets : dict or None
            If specified, only the specified targets will be rendered.
            This is a dict with the extension as keys and the target_filepath
            (as a render path) as the value.
        create_dirs : bool, optional
            Create directories for the rendered target files, if the directories
            don't exist.
        update_only : bool, optional
            If True, the file will only be rendered if the rendered file is
            older than the source file.
        subdocuments : bool, optional
            If True, the subdocuments will be rendered (first) as well.

        Returns
        -------
        bool
            True, if the document needed to be rendered.
            False, if the document did not need to be rendered.

        """
        if subdocuments:
            for doc in self.documents_list(only_subdocuments=True):
                doc.render(targets=targets, create_dirs=create_dirs,
                                update_only=update_only)

        # Workup the targets into a dict, like self.targets
        if targets is None:
            targets = self.targets
        elif isinstance(targets, dict):
            pass
        else:
            msg = "Specified targets '{}' must be a dict"
            raise DocumentError(msg.format(targets))

        # Check to see if the target directories need to be created
        if create_dirs:
            for target_filepath in targets.values():
                mkdir_p(target_filepath)

        # Process each specified target
        for target, target_filepath in targets.items():
            target = target if target.startswith('.') else '.' + target

            # Skip if we should update_only and the src_filepath is older
            # than the target_filepath, if target_filepath exists.
            if update_only and not self.render_required(target_filepath):
                continue

            # Get the ast
            if 'collection' == self.context.get('render', None):
                ast = self.get_grouped_asts(target=target)
            else:
                ast = self.get_ast()

            # Determine whether it's a compiled target or uncompiled target
            if target in settings.compiled_exts:
                self.render_compiled(target=target,
                                     target_filepath=target_filepath,
                                     targets=targets,
                                     ast=ast)
            else:
                self.render_uncompiled(target=target,
                                       target_filepath=target_filepath,
                                       ast=ast)

        return True

    def render_uncompiled(self, target, target_filepath, ast=None):
        """Render a text target format.

        For many output formats, like .html and .tex, the rendered file is
        simply another text file. This render_uncompiled method handles these.

        The rending has the following steps:

        *Asynchronous*.
        Depends only on the source file and does not depend on variables from
        other documents in the context. Consequently, it can be run in
        a multi-threaded mode, and this part does not need to be repeated as
        long as the source file has not changed.

            1. get_ast (:meth:`get_ast`)

        **After this step** for all documents, the `context` is populated.
        Nothing in the subsequent steps should change these.

        *Synchronous*.
        The synchronous step depends on the target type as well as the
        global_context. Consequently, all other documents in a tree must be
        loaded and their ASTs processed to conduct this step.

            2. convert to the target type

                a. Convert the AST to target string using an AST conversion
                   function.

                b. Render this string in a template.

        Parameters
        ----------
        target: str
            The target extension to render. ex: '.html' or '.tex'
        target_filepath: str
            The final render path of the target file. ex : 'html/index.html'
        ast : list or tag, optional
            If specified, use the given AST instead of the one from the get_ast
            method.
        """
        # Step 1: Asynchronous
        # get the ast
        if ast is None:
            ast = self.get_ast()

        # Step 2: Synchronous

        # Prepare the context

        # Add non-private variables from the  context
        context = {k: v for k, v in self.context.items()
                   if not str(k).startswith("_")}

        # Further process the context. The context_processors render target-
        # specific information.
        for processor in self.context_processors:
            processor(context, target)

        # render and save to output file
        target_name = target.strip('.')

        # Set the body variable to the AST
        context['body'] = ast

        # Get a template. Reload is set to True to make sure that the latest
        # version of the template is loaded.
        template = self.get_template(target=target, reload=True)

        # If a template is available, use it to render the string.
        # Otherwise, just write the string

        if template is not None:
            # generate a new ouput_string
            output_string = template.render(**context)

            # Add template to dependencies, if able
            if ('dependency_manager' in self.context and
                    hasattr(template, 'filename')):
                dep = self.context['dependency_manager']

                # See if the dependencies has a method for this target
                meth = getattr(dep, 'add_' + target_name, None)
                if meth is not None:
                    meth(output_string)
        else:
            if hasattr(ast, target_name):
                output_string = getattr(ast, target_name)
            else:
                output_string = ast.default

        # Write the file
        with open(target_filepath, 'w') as f:
            f.write(output_string)

    def render_compiled(self, target, target_filepath, targets, ast=None):
        """Render a compiled target format.

        For some formats, like .pdf, these have to be compiled after generating
        the text file from the render_uncompiled method. The render_compiled
        method generates the needed intermediate text file and converts it to
        the final output format.

        Parameters
        ----------
        target: str
            The target extension to render. ex: '.pdf'
        target_filepath : str
            The final render path of the target file. ex : 'pdf/index.pdf'
        targets : dict
            This is a dict with the extension as keys and the target_filepath
            (as a render path) as the value.
        ast : list or tag, optional
            If specified, use the given AST instead of the one from the get_ast
            method.
        """
        # Render the intermediate target. First, see if the
        # intermediary extension is already in targets. If not, create
        # a temporary one.
        inter_ext = settings.compiled_exts[target]
        if inter_ext in targets:
            inter_target_filepath = targets[inter_ext]
            self.render_uncompiled(target=inter_ext,
                                   target_filepath=inter_target_filepath,
                                   ast=ast)
            src_filepath = inter_target_filepath
        else:
            temp_dir = self.temp_dir
            temp_filename = os.path.split(target_filepath)[1]
            temp_filename = (os.path.splitext(temp_filename)[0] +
                             inter_ext)
            temp_path = os.path.join(temp_dir, temp_filename)
            self.render_uncompiled(target=inter_ext,
                                   target_filepath=temp_path,
                                   ast=ast)
            src_filepath = temp_path

        # Now convert the file and continue
        target_basefilepath = os.path.splitext(target_filepath)[0]
        filepath = convert(src_filepath=src_filepath,
                           target_basefilepath=target_basefilepath,
                           targets=[target])
