"""
Classes and functions for rendering documents.
"""
from collections import OrderedDict
from weakref import ref
from tempfile import mkdtemp
from shutil import rmtree
import os
import os.path

from ..ast import process_ast, process_paragraphs, process_typography
from ..templates import get_template
from ..header import load_yaml_header
from ..macros import replace_macros
from ..convert import convert
from ..labels import LabelManager
from ..dependency_manager import DependencyManager
from ..tags.toc import process_context_toc
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
    sub_documents : :obj:`collections.OrderedDict`
        A dict with the sub-documents included in this document. The keys are
        src_filepath values relative to the document's directory, and the values
        are the sub_documents themselves.

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
        A list of functions to process the document's context *after* the
        AST is loaded. The context_processor functions only take a context as
        a parameter.
    """

    src_filepath = None
    context = None
    sub_documents = None
    _parent_context = None
    _label = None
    _target_root = None
    _target_list = None
    _temp_dir = None

    string_processors = [load_yaml_header,  # Process YAML headers
                         replace_macros,  # Process macros
                         ]
    ast_processors = [process_ast,
                      process_paragraphs,
                      process_typography,
                      ]
    context_processors = [process_context_toc,
                          ]

    def __init__(self, src_filepath, target_root=None, context=None):
        self.src_filepath = str(src_filepath)
        self.sub_documents = OrderedDict()
        self.context = dict()

        self._parent_context = context
        src_path = os.path.split(self.src_filepath)[0]
        self._target_root = (target_root if target_root is not None else
                             os.path.split(src_path)[0])

        # Reset the local_context, dependencies and labels
        self.reset_contexts()
        self.reset_dependencies()
        self.reset_labels()

        # The cached AST
        self._ast = None

        # The last modification time of the document since its AST was last
        # processed
        self._mtime = None

        # Read in the AST
        self.get_ast()

    def __del__(self):
        """Clean up any temp directories no longer in use."""
        if self._temp_dir is not None:
            rmtree(self._temp_dir, ignore_errors=True)

    @property
    def title(self):
        """The title for the document."""
        if 'title' in self.context:
            return self.context['title']
        return self.src_filepath.strip(settings.document_extension)

    @property
    def short(self):
        """The short title for the document."""
        if 'short' in self.context:
            return self.context['short']
        else:
            return self.title

    @property
    def number(self):
        """The number of the document."""
        if ('documents' in self.context and
           self.src_filepath in self.context['documents']):

            documents = list(self.context['documents'].keys())
            return documents.index(self.src_filepath) + 1
        else:
            return None

    @property
    def temp_dir(self):
        if self._temp_dir is None:
            self._temp_dir = mkdtemp()
        return self._temp_dir

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
        if self._target_list is None:
            # Get the target list from the context
            self.target_list = self.context['targets']

        if isinstance(self._target_list, list):
            return self._target_list
        else:
            return []

    @target_list.setter
    def target_list(self, value):
        """Set the target_list, which is a list of target extensions with a
        trailing period."""
        if isinstance(value, list):
            target_list = value
        elif isinstance(value, str):
            # If it's a string, items may be separated by commas, spaces
            # or both
            target_exts = value.split(',')
            if len(target_exts) == 1:
                target_list = [t.strip() for t in
                                     target_exts[0].split(" ")]
            else:
                target_list = [t.strip() for t in target_exts]

        else:
            raise AttributeError

        # Prepend the targets with a period. ex: '.html'
        target_list = ['.' + t if not t.startswith('.') else t
                       for t in target_list]
        self._target_list = target_list

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
        base_filename = os.path.split(self.src_filepath)[1]
        base_filename = os.path.splitext(base_filename)[0]
        for target_ext, stripped_ext in zip(target_list, stripped_exts):
            t = (os.path.join(base_target, stripped_ext, base_filename) +
                 target_ext)
            targets[target_ext] = t
        self._targets = targets
        return self._targets

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
            target_root = self.target_root + "/" + target.strip('.')
            return os.path.relpath(self.targets[target], target_root)

        return self.targets[target]

    def reset_contexts(self):
        """Clear and repopulate the local_context and global_context."""
        # Remove everything from the context dict except for objects that
        # need to be preserved between documents, like the label_manager and
        # dependency_manager
        excluded_items = ('label_manager', 'dependency_manager')
        context_keys = list(self.context.keys())
        for k in context_keys:
            if k in excluded_items:
                continue
            del self.context[k]

        # Copy over the context values from parent context. The excluded_items
        # do not pertain to sub-documents.
        excluded_items = ('include',)
        if self._parent_context is not None:
            for k, v in self._parent_context.items():
                if k in excluded_items:
                    continue
                self.context[k] = v

        self.context['document'] = self

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
        if 'documents' not in self.context:
            self.context['documents'] = OrderedDict()

        # Add this document to the documents weak refs ordered dict
        self.context['documents'][self.src_filepath] = ref(self)

        # project_root, target_root. Include methods with 'render' options

    def reset_dependencies(self):
        """Clear and repopulate the dependencies for this document in the
        dependency manager."""
        if 'dependency_manager' in self.context:
            document_src_filepath = self.src_filepath
            dep = self.context['dependency_manager']
            dep.reset(document_src_filepath=document_src_filepath)

    def reset_labels(self):
        """Clear and repopulate the labels for this document in the label
        manager."""
        if 'label_manager' in self.context:
            label_manager = self.context['label_manager']
            label_manager.reset(document=self)

    def set_document_label(self):
        """Set the label for this document in the label manager.

        .. note:: This function is invoked as part of the get_ast method, after
                  parsing the source file, so that the 'title' attribute can be
                  retrieved from the local_context.
        """
        if 'label_manager' in self.context and self._label is None:
            label_manager = self.context['label_manager']

            # Get the filepath for this document relative to the project_root,
            # if possible
            project_filepath = os.path.relpath(self.src_filepath,
                                               self.project_root)

            # Get the level of the document
            level = self.context.get('level', 1)

            # Set the label for this document
            kind = ('document', 'document-level-' + str(level))
            label = label_manager.add_label(document=self, kind=kind,
                                            id='doc:' + project_filepath)
            self._label = label

    def load_sub_documents(self):
        """Load the sub-documents listed in the include of a local_context."""
        if 'include' in self.context:
            src_filepaths = self.context['include']
            if isinstance(src_filepaths, str):
                src_filepaths = src_filepaths.split()
            src_filepaths = [s for s in src_filepaths if isinstance(s, str)]

            # Create missing documents
            current_src_filepath = os.path.split(self.src_filepath)[0]
            for src_filepath in src_filepaths:
                if src_filepath in self.sub_documents:
                    continue

                # Add the current path to make it a render_path
                a_src_filepath = os.path.join(current_src_filepath,
                                              src_filepath)

                doc = Document(src_filepath=a_src_filepath,
                               context=self.context)
                self.sub_documents[src_filepath] = doc

            # Remove missing documents
            extra_src_filepaths = (src_filepaths ^
                                   self.sub_documents.keys())
            for src_filepath in extra_src_filepaths:
                del self.sub_documents[src_filepath]

    # TODO: Keep track of ast modification times in the context so that this
    # can be used with update_only on render.
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
        reload : bool, str
            If True, force the reload of the AST.

        Returns
        -------
        :obj:`disseminate.tag.Tag`
            A root tag object for the AST.
        """
        # Run get_ast for the sub-documents
        for document in self.sub_documents.values():
            document.get_ast(reload=reload)

        # Check to make sure the file exists
        if not os.path.isfile(self.src_filepath):  # file must exist
            msg = "The source document '{}' must exist."
            raise DocumentError(msg.format(self.src_filepath))

        stat = os.stat(self.src_filepath)
        time = stat.st_mtime

        # Update the AST, if needed
        if (getattr(self, '_ast', None) is None or
           getattr(self, '_mtime', None) is None or
           time > self._mtime or
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

            # Clear the labels for this document
            self.reset_labels()

            # Process the string
            for processor in self.string_processors:
                string = processor(string, self.context)

            # Process and validate the AST
            ast = string
            for processor in self.ast_processors:
                ast = processor(ast=ast, context=self.context,
                                src_filepath=self.src_filepath)

            # Set the label for this document. This is done after the source
            # file is parsed because the source file might contain the 'title'
            # setting.
            self.set_document_label()

            # Load the sub-documents
            self.load_sub_documents()

            # Further process the context. These may depend on the document's
            # label of the sub-documents, so it is run after these are loaded.
            for processor in self.context_processors:
                processor(self.context)

            # cache the ast
            self._ast = ast
            self._mtime = time

        return self._ast

    def render(self, targets=None, create_dirs=settings.create_dirs,
               update_only=True):
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

        Returns
        -------
        bool
            True, if the document needed to be rendered.
            False, if the document did not need to be rendered.

        """
        # Workup the targets into a dict, like self.targets
        if targets is None:
            targets = self.targets
        elif isinstance(targets, dict):
            pass
        else:
            msg = "Specified targets '{}' must be a dict"
            raise DocumentError(msg.format(targets))

        # Process the sub-documents
        for document in self.sub_documents.values():
            document.render(targets=targets, create_dirs=create_dirs,
                            update_only=update_only)

        # Check to see if the target directories need to be created
        if create_dirs:
            for target_filepath in targets.values():
                mkdir_p(target_filepath)

        # Process each specified target
        for target, target_filepath in targets.items():
            target = target if target.startswith('.') else '.' + target

            # Skip if we should update_only and the src_filepath is older
            # than the target_filepath, if target_filepath exists.
            if (update_only and
                    os.path.isfile(target_filepath) and
                    (os.path.getmtime(self.src_filepath) <=
                     os.path.getmtime(target_filepath))):
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
        """
        # Step 1: Asynchronous
        # get the ast
        ast = self.get_ast()

        # Step 2: Synchronous

        # First pull out the template, if specified
        template_basename = settings.template_basename
        if 'template' in self.context:
            template_basename = self.context['template']

        # Prepare the context
        # Add non-private variables from the  context
        context = {k: v for k, v in self.context.items()
                   if not str(k).startswith("_")}

        # render and save to output file
        target_name = target.strip('.')

        if hasattr(ast, target_name):
            output_string = getattr(ast, target_name)()
        else:
            output_string = ast.default()

        # Add the output string to the context
        context['body'] = output_string

        # get a template. The following can be done asynchronously.
        template = get_template(self.src_filepath, target=target,
                                template_basename=template_basename)

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

        # determine whether the file contents are new
        if not os.path.isfile(target_filepath):
            new = True
        else:
            with open(target_filepath, 'r') as f:
                new = output_string != f.read()

        # if the contents are new, write it to the file
        if new:
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
        targets : dict or None
            If specified, only the specified targets will be rendered.
            This is a dict with the extension as keys and the target_filepath
            (as a render path) as the value.
        """
        # Render the intermediate target. First, see if the
        # intermediary extension is already in targets. If not, create
        # a temporary one.
        inter_ext = settings.compiled_exts[target]
        if inter_ext in targets:
            self.render_uncompiled(target=inter_ext,
                                   target_filepath=target_filepath)
            src_filepath = targets[inter_ext]
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
        convert(src_filepath=src_filepath,
                target_basefilepath=target_basefilepath,
                targets=[target, ])