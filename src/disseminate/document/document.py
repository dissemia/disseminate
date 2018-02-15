"""
Classes and functions for rendering documents.
"""
import os
import os.path

from ..ast import process_ast
from ..templates import get_template
from ..header import load_yaml_header
from ..macros import replace_macros
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
    targets : dict
        A dict with the target extension as keys (ex: '.html') and the value
        is the target_filepath for that target. (ex: 'html/index.html')
    global_context : dict, optional
        The global context to store variables shared between all documents.

    Attributes
    ----------
    src_filepath : str
        A filename for a document (markup source) file. This file should exist.
        This path is a render path: it's either an absolute path or a path
        relative to the current directory.
    targets : dict
        A dict with the target extension as keys (ex: '.html') and the value
        is the target_filepath for that target. (ex: 'html/index.html')
        These paths are render paths: they're either an absolute path or a
        path relative to the current directory.
    local_context : dict
        The context with values for the current document. The values in this
        dict do not depend on values from other documents. (local)
    global_context : dict
        The context with values for all documents in a project. The
        `global_context` is constructed with the `src_filepath` as a key and
        the `local_context` as a value.

    string_processors : list of functions, **class attribute**
        A list of functions to process the string before conversion to the
        AST. These functions are executed in sequence and simply accept the
        string, local_context and global_context as arguments and return a
        processed string.

        .. note:: String processors are run asynchronously, and the
                  local_context and global_context dicts may not be fully
                  populated.

    ast_processors : list of functions, **class attribute**
        A list of functions to process the AST. These functions are executed in
        sequence and simply accept a AST argument and return a processed AST.

        .. note:: AST processors are run asynchronously, and the
                  local_context and global_context dicts may not be fully
                  populated.
    """

    src_filepath = None
    targets = None
    local_context = None
    global_context = None

    string_processors = [load_yaml_header,  # Process YAML headers
                         replace_macros,  # Process macros
                         ]
    ast_processors = [process_ast,
                      ]
    ast_post_processors = []

    def __init__(self, src_filepath, targets, global_context=None):
        self.src_filepath = src_filepath
        self.targets = targets
        self.global_context = (global_context
                               if isinstance(global_context, dict) else dict())
        self.local_context = self.global_context.setdefault(src_filepath,
                                                            dict())
        # The cached AST
        self._ast = None

        # The last modification time of the document since its AST was last
        # processed
        self._mtime = None

    def reset_contexts(self):
        """Clear and repopulate the local_context and global_context."""
        self.local_context.clear()
        # Populate the document's src_filepath
        self.local_context['_src_filepath'] = self.src_filepath

        # Set this document's number in the tree, if available
        if ('_document_numbers' in self.global_context and
            self.src_filepath in self.global_context['_document_numbers']):
            document_numbers = self.global_context['_document_numbers']
            document_number = document_numbers[self.src_filepath]
            self.local_context['document_number'] = document_number

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

            # TODO: Reorganize the resetting of contexts
            # Reset the local_context. When reloading an AST, the old
            # local_context is invalidated since some of the entries may have
            # changed
            self.reset_contexts()

            # Clear the dependencies for this document
            if '_dependencies' in self.global_context:
                document_src_filepath = self.src_filepath
                dep = self.global_context['_dependencies']
                dep.reset(document_src_filepath=document_src_filepath)

            # Process the string
            for processor in self.string_processors:
                string = processor(string, self.local_context,
                                   self.global_context)

            # Process and validate the AST
            ast = [string]
            for processor in self.ast_processors:
                ast = process_ast(ast=ast, local_context=self.local_context,
                                  global_context=self.global_context,
                                  src_filepath=self.src_filepath)

            # cache the ast
            self._ast = ast
            self._mtime = time

        return self._ast

    def render(self, targets=None, create_dirs=settings.create_dirs):
        """Convert the src_filepath to a rendered document at target_filepath.

        A document loads a document (source markup) file and this method
        renders it to one or more target output format(s).

        The rending has the following steps:

        *Asynchronous*.
        Depends only on the source file and does not depend on variables from
        other documents in the global_context. Consequently, it can be run in
        a multi-threaded mode, and this part does not need to be repeated as
        long as the source file has not changed.

            1. get_ast (:meth:`get_ast`)

                a. Load the file into a string

                b. Process the string with the string processors
                   (`self.string_processors`).

                c. Convert the string to an AST.

                d. Process the AST with the ast processors
                   (`self.ast_processors`). These modifications do not depend
                   on the global_context or the target type.

        **After this step** for all documents, the `local_context` and
        `global_context` are fully populated. Nothing in the subsequent steps
        should change these.

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
        targets : str or list of str
            If specified, only the specified targets will be rendered.
            Otherwise all targets in self.targets will be rendered.
        create_dirs : bool, optional
            Create directories for the rendered target files, if the directories
            don't exist.

        Returns
        -------
        bool
            True, if the document needed to be rendered.
            False, if the document did not need to be rendered.

        """
        # Workup the targets into a dict, like self.targets
        if targets is None:
            targets = self.targets
        elif isinstance(targets, str):
            if targets not in self.targets:
                msg = ("The target format '{}' is not available in this "
                       "document's available targets.")
                raise DocumentError(msg.format(targets))
            targets = {targets: self.targets[targets]}
        elif isinstance(targets, list):
            targets = {t: self.targets[t] for t in targets}
        else:
            msg = "Specified targets '{}' must be a string or a list of strings"
            raise DocumentError(msg.format(targets))

        # Process each specified target
        for target, target_filepath in targets.items():
            target = target if target.startswith('.') else '.' + target

            # Check to see if the target directory needs to be created
            if create_dirs:
                mkdir_p(target_filepath)

            # Step 1: Asynchronous
            # get the ast
            ast = self.get_ast()

            # Step 2: Synchronous
            # Run individual tag process functions
            # At this stage, the tags may depend on other documents through the
            # global_context. (i.e. it must be done synchronously

            # postprocess_ast

            # First pull out the template, if specified
            template_basename = settings.template_basename
            if 'template' in self.global_context:
                template_basename = self.global_context['template']
            if 'template' in self.local_context:
                template_basename = self.local_context['template']

            # Prepare the context
            # Add non-private variables from the global context
            # context['_global'] = self.global_context
            context = {k: v for k, v in self.global_context.items()
                       if not str(k).startswith("_")}

            # Add non-private variables from the local_context
            # These intentionally overwrite overlapping variables from the
            # global_context
            context.update({k: v for k, v in self.local_context.items()
                            if not str(k).startswith("_")})

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
                if ('_dependencies' in self.global_context and
                    hasattr(template, 'filename')):
                    dep = self.global_context['_dependencies']

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

        return True
