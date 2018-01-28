"""
Classes and functions for rendering documents.
"""
import os
import os.path

from .ast import process_ast
from .tags import Tag
from .templates import get_template
from .utils import mkdir_p
from . import settings


def process_tag_ast(ast, target):
    """Invoke the 'process_ast' method of tags, if available.

    Parameters
    ----------
    ast: list of str and :obj:`disseminate.Tag` objects.
        An Abstract Syntax Tree (AST) to process in place.

    Returns
    -------
    processed_ast : list of str and :obj:`disseminate.Tag` objects.
        A processed AST.
    """
    processed_ast = []
    for item in processed_ast:
        if (isinstance(item, Tag) and
           getattr(item, 'process_ast', None) is not None):
            new_item = item.process_ast(target)
            processed_ast += [new_item, ]
        elif isinstance(item, list):
            processed_ast += process_tag_ast(item, target)
        else:
            processed_ast.append(item)

    return processed_ast


class DocumentError(Exception):
    """An error generated while loading and processing a document."""
    pass


class Document(object):
    """A document rendered from a source file to a target file.

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
    targets : dict
        A dict with the target extension as keys (ex: '.html') and the value
        is the target_filepath for that target. (ex: 'html/index.html')
    local_context : dict
        The context with values for the current document. The values in this
        dict do not depend on values from other documents. (local)
    global_context : dict
        The context with values for all documents in a project. The
        `global_context` is constructed with the `src_filepath` as a key and
        the `local_context` as a value.

    string_processors : list of functions, **class attribute**
        A list of functions to process the string before conversion to the
        AST. These functions are executed in sequence and simply accept a
        string argument and return a processed string.

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

    string_processors = []
    ast_processors = []
    ast_post_processors = []

    def __init__(self, src_filepath, targets, global_context=None):
        self.src_filepath = src_filepath
        self.targets = targets
        self.global_context = (global_context
                               if isinstance(global_context, dict) else dict())
        self.local_context = self.global_context.setdefault(src_filepath,
                                                            dict())
        # Private variables
        self._ast = None
        self._mtime = None

    def get_ast(self):
        """Process and return the AST.

        This method generates and caches the AST. This step is conducted
        asynchronously. (i.e. the local_context and global_context may not be
        completed populated while the AST is processed.)

        The cached AST is updated if the source file is updated.

        See the :meth:`render` method for more details.
        """
        # Check to make sure the file exists
        if not os.path.isfile(self.src_filepath):  # file must exist
            msg = "The source document '{}' must exist."
            raise DocumentError(msg.format(self.src_filepath))

        stat = os.stat(self.src_filepath)
        time = stat.st_mtime

        if (getattr(self, '_ast', None) is None or
           getattr(self, '_mtime', None) is None or
           time > self._mtime):
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

            # Process the string
            for processor in self.string_processors:
                string = processor(string)

            # Process and validate the AST
            ast = process_ast(s=string, local_context=self.local_context,
                              global_context=self.global_context,
                              src_filepath=self.src_filepath)

            # Run the AST processing functions
            for processor in self.ast_processors:
                ast = processor(ast)

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

            # render and save to output file
            target_name = target.strip('.')
            if hasattr(ast, target_name):
                output_string = getattr(ast, target_name)()
            else:
                output_string = ast.default()

            # get a template. The following can be done asynchronously.
            template = get_template(self.src_filepath, target=target)

            if template is not None:
                # copy the local_context
                context = dict(self.local_context)

                # add the global context
                context['_global'] = self.global_context

                # set additional variables needed for the template
                context['body'] = output_string

                # generate a new ouput_string
                output_string = template.render(**context)

                with open(target_filepath, 'w') as f:
                    f.write(output_string)

        return True
