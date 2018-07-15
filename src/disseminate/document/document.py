"""
Classes and functions for rendering documents.
"""
from tempfile import mkdtemp
from shutil import rmtree
from collections import OrderedDict
import logging
import os
import os.path

from .document_context import DocumentContext
from ..ast import (process_context_asts, process_context_paragraphs,
                   process_context_typography)
from ..templates import get_template
from ..header import load_header
from ..macros import process_context_macros
from ..convert import convert
from ..context.utils import context_targets, context_includes
from ..utils import mkdir_p
from .. import settings


class DocumentError(Exception):
    """An error generated while loading and processing a document."""
    pass


class Document(object):
    """A base class document rendered from a source file to one or more
    target files.

    Parameters
    ----------
    src_filepath : str
        The path (a render path, relative to the current directory or an
        absolute path) for the document (markup source) file of this document.
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
    context: :obj:`disseminate.document.DocumentContext`
        A context dict with the values needed to render a target document.
    subdocuments : :collections:`OrderedDict`
        An ordered dict with the sub-documents included in this document.
        The keys are src_filepath values as render paths, and the values
        are the subdocuments themselves. The documents are ordered according
        to their placement in the document tree.

        This document owns the subdocuments and only weak references to these
        documents should be made. (i.e. when the subdocuments dict is cleared,
        the memory for the document objects should be released)
    processors : list of functions, **class attribute**
        A list of functions to process the context. These functions are
        executed in sequence and simply accept a context dict.
    """

    src_filepath = None
    context = None
    subdocuments = None

    #: Context processors
    #: def processor(context)
    processors = [
        # Process header. This should be loaded first or near the very start
        # since it loads in the values in the context (other than body)
        load_header,
        # Process macros. This will convert macros in the context that have
        # just been loaded from the header
        process_context_macros,
        # Process the ASTs in the context. ASTs are simply nested trees of Tag
        # objects. After the header and context are loaded and prepared, this
        # function converts the entry values in the context to ASTs, if it can.
        process_context_asts,
        # Process AST paragraphs. After the appropriate context values have
        # been converted to ASTs, go through these ASTs and identify and tag
        # paragraphs.
        process_context_paragraphs,
        # Process the AST typography. After the appropriate context values have
        # been converted to ASTs, identify the appropriate typography elements
        # like quotes, endashes and emdashes.
        process_context_typography,
                  ]

    #: The directory for the root document of a project (a document and its
    #: subdocuments.
    _project_root = None

    #: The calculated target_root, based on the value specified or a value
    #: evaluated from the project_root
    _target_root = None

    #: The path of a temporary directory created for this document, if needed.
    _temp_dir = None

    #: Cached template objects for this document.
    _templates = None

    def __init__(self, src_filepath, target_root=None, parent_context=None):
        logging.debug("Creating document: {}".format(src_filepath))

        # Populate the attributes
        self.src_filepath = str(src_filepath)
        self.subdocuments = OrderedDict()
        self._templates = dict()
        src_path = os.path.split(self.src_filepath)[0]

        # Set the project_root, if needed.
        if parent_context is None or 'project_root' not in parent_context:
            self._project_root = src_path

        # Set the target_root, if needed.
        if target_root is not None:
            # Use the specified value, if available.
            self._target_root = target_root
        elif parent_context is not None and 'target_root' in parent_context:
            # Otherwise use the one in the parent context, if available.
            self._target_root = parent_context['target_root']
        # In these situations, there is no 'target_root' in the parent context,
        # so we have to figure one out.
        elif src_path.endswith(settings.document_src_directory):
            # If the src_path is in a src_directory, use the directory above
            # this directory
            self._target_root = os.path.split(src_path)[0]
        else:
            # Otherwise just use the same directory as the src directory
            self._target_root = src_path

        # Create the context
        self.context = DocumentContext(document=self,
                                       parent_context=parent_context)

        # Read in the document and load sub-documents
        self.load_document()

    def __del__(self):
        """Clean up any temp directories no longer in use."""
        if self._temp_dir is not None:
            rmtree(self._temp_dir, ignore_errors=True)

        # Reset the labels and dependencies for this document
        self.reset_labels()
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
        return (self._project_root if self._project_root is not None else
                self.context.get('project_root', None))

    @property
    def target_root(self):
        return (self._target_root if self._target_root is not None else
                self.context.get('target_root', None))

    @property
    def target_list(self):
        """The list of targets from the context."""
        return context_targets(self.context)

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
        """Load, clear and reset the context.

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
          1. include: the sub-documents to include under a document.
          2. title: the title of a document.
          3. short: the short title of a document.
          4. document: a weakref to this document.
          5. mtime: The modification time of the source document. This is
             populated by the get_ast method.
        """
        self.context.reset()

    @property
    def dependency_manager(self):
        return self.context.get('dependency_manager', None)

    def reset_dependencies(self):
        """Clear and repopulate the dependencies for this document in the
        dependency manager."""
        if 'dependency_manager' in self.context:
            document_src_filepath = self.src_filepath
            dep = self.context['dependency_manager']
            dep.reset(document_src_filepath=document_src_filepath)

    @property
    def label_manager(self):
        return self.context.get('label_manager', None)

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

        # Retrieve the file paths of included files in the context, as render
        # paths
        src_filepaths = context_includes(context=self.context,
                                         render_paths=True)

        for src_filepath in src_filepaths:
            # If the document is already loaded, copy it to the subdocuments
            # ordered dict
            if src_filepath in root_dict:
                subdoc = root_dict[src_filepath]

                if self.src_filepath not in subdoc.subdocuments:
                    self.subdocuments[src_filepath] = subdoc
                continue

            # The document could not be found, at this point. Create it.

            # Create the document and add it to the subdocuments ordered
            # dict.
            subdoc = Document(src_filepath=src_filepath,
                              parent_context=self.context)
            self.subdocuments[src_filepath] = subdoc

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

    # TODO: rename to load(...)
    def load_document(self, reload=False):
        """Load or reload the document into the context.

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

        # Update the context, if needed
        body_attr = settings.body_attr
        if (self.context.get(body_attr, None) is None or
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

            # Reset the local_context. When reloading an AST, the old
            # local_context is invalidated since some of the entries may have
            # changed
            self.reset_contexts()

            # Clear the dependencies for this document
            self.reset_dependencies()

            # Reset the registered labels for this document and set the
            # document's label
            self.reset_labels()

            # Load the string from the src_filepath,
            with open(self.src_filepath) as f:
                string = f.read()

            # Place the text of the string in the 'body' attribute of the
            # context (see settings.body_attr)
            body_attr = settings.body_attr
            self.context[body_attr] = string

            # Process the context
            for processor in self.processors:
                processor(self.context)

            # Load the sub-documents. This is done after processing the string
            # and ast since these may include sub-files, which should be read
            # in before being loaded.
            self.load_subdocuments()

            # Reset the modification time with the current modification time of
            # the document.
            self.context['mtime'] = time

        # Run 'load_document' for the sub-documents. This should be done after
        # loading this documentsince this document's header may have includes
        for document in self.documents_list(only_subdocuments=True):
            document.load_document(reload=reload)

        return None

    def render_required(self, target_filepath):
        """Evaluate whether a render is required to write the target file.

        .. note:: This method re-loads the documents since it checks the
                  modification time of tags in the context, which may become
                  updated if the source file (or other source files) are
                  updated.

        Parameters
        ----------
        target_filepath : The render path for the target file.

        Returns
        -------
        render_required : bool
            True, if a render is required.
            False if a render isn't required.
        """
        # Reload document
        self.load_document()

        # Setup variables
        target = os.path.splitext(target_filepath)[1]

        # 1. A render is required if the target_filepath doesn't exist
        if not os.path.isfile(target_filepath):
            logging.debug("Render required for {}: '{}' target file "
                          "does not exist.".format(self, target_filepath))
            return True

        # Get the modification time for the source file(s) (src_filepath)
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
        tag_mtimes = [t.mtime for t in self.context.values()
                      if hasattr(t, 'mtime')]
        max_tag_mtime = max(tag_mtimes) if len(tag_mtimes) > 0 else None
        if max_tag_mtime is not None and target_mtime < max_tag_mtime:
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
            # The 'render_required' also reloads the document.
            if not self.render_required(target_filepath) and update_only:
                continue

            # Determine whether it's a compiled target or uncompiled target
            if target in settings.compiled_exts:
                self.render_compiled(target=target,
                                     target_filepath=target_filepath,
                                     targets=targets)
            else:
                self.render_uncompiled(target=target,
                                       target_filepath=target_filepath)

        return True

    def render_uncompiled(self, target, target_filepath):
        """Render a text target format.

        For many output formats, like .html and .tex, the rendered file is
        simply another text file. This render_uncompiled method handles these.

        Parameters
        ----------
        target: str
            The target extension to render. ex: '.html' or '.tex'
        target_filepath: str
            The final render path of the target file. ex : 'html/index.html'
        """
        # Prepare the filename to render and save to output file
        target_name = target.strip('.')

        # Get a template. Reload is set to True to make sure that the latest
        # version of the template is loaded.
        template = self.get_template(target=target, reload=True)

        # If a template is available, use it to render the string.
        # Otherwise, just write the string

        if template is not None:
            # generate a new ouput_string
            output_string = template.render(**self.context)

            # Add template to dependencies, if able
            if ('dependency_manager' in self.context and
                    hasattr(template, 'filename')):
                dep = self.context['dependency_manager']

                # See if the dependencies has a method for this target
                meth = getattr(dep, 'add_' + target_name, None)
                if meth is not None:
                    meth(output_string)
        else:
            # If there is no template, simply use the context's body tag as the
            # string
            body_attr = settings.body_attr
            body = self.context.get(body_attr, None)
            if hasattr(body, target_name):
                output_string = getattr(body, target_name)
            elif hasattr(body, 'default'):
                output_string = getattr(body, 'default')
            else:
                output_string = body

        # Write the file
        with open(target_filepath, 'w') as f:
            f.write(output_string)

    def render_compiled(self, target, target_filepath, targets):
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
        """
        # Render the intermediate target. First, see if the
        # intermediary extension is already in targets. If not, create
        # a temporary one.
        inter_ext = settings.compiled_exts[target]
        if inter_ext in targets:
            inter_target_filepath = targets[inter_ext]
            self.render_uncompiled(target=inter_ext,
                                   target_filepath=inter_target_filepath)
            src_filepath = inter_target_filepath
        else:
            temp_dir = self.temp_dir
            temp_filename = os.path.split(target_filepath)[1]
            temp_filename = (os.path.splitext(temp_filename)[0] +
                             inter_ext)
            temp_path = os.path.join(temp_dir, temp_filename)
            self.render_uncompiled(target=inter_ext,
                                   target_filepath=temp_path)
            src_filepath = temp_path

        # Now convert the file and continue
        target_basefilepath = os.path.splitext(target_filepath)[0]
        filepath = convert(src_filepath=src_filepath,
                           target_basefilepath=target_basefilepath,
                           targets=[target])
