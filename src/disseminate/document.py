"""
Classes and functions for rendering documents.
"""
import os
import os.path

from .ast import process_ast, conversions
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
        The context with values for the current document. (local)
    global_context : dict
        The context with values for all documents in a project. (global)

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
        self.local_context = dict()
        self.global_context = (global_context
                               if isinstance(global_context, dict) else dict())

        # Private variables
        self._ast = None

    def get_ast(self):
        """Process and return the AST.

        This method generates and caches the AST. This step is conducted
        asynchronously. (i.e. the local_context and global_context may not be
        completed populated while the AST is processed.)
        """
        if getattr(self, '_ast', None) is None:
            # Check to make sure the file is reasonable
            if not os.path.isfile(self.src_filepath):  # file must exist
                msg = "The source document '{}' must exist."
                raise DocumentError(msg.format(self.src_filepath))
            filesize = os.stat(self.src_filepath).st_size
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

            self._ast = ast

        return self._ast

    def render(self, targets=None,
               update_only=settings.update_only,
               create_dirs=settings.create_dirs):
        """Convert the src_filepath to a rendered document at target_filepath.

        .. note:: This function is run synchronously.

        Parameters
        ----------
        targets : str or list of str
            If specified, only the specified targets will be rendered.
            Otherwise all targets in self.targets will be rendered.
        update_only : bool, optional
            Only render the file if the target doesn't exist or the target file
            is older than the source file.
        create_dirs : bool, optional
            Create directories for the rendered target files, if the directories
            don't exist.

        Returns
        -------
        bool
            True, if the render was successful.
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

            # Check to see if the source file needs to be updated
            if (update_only and os.path.isfile(target_filepath) and
                    (os.stat(self.src_filepath).st_mtime >
                     os.stat(target_filepath).st_mtime)):
                return True

            # Check to see if the target directory needs to be created
            if create_dirs:
                mkdir_p(target_filepath)

            # get the ast
            ast = self.get_ast()

            # Run individual tag process functions
            # At this stage, the tags may depend on other documents through the
            # global_context. (i.e. it must be done synchronously

            # postprocess_ast

            # render and save to output file
            convert_func = conversions.get(target, None)
            output_string = convert_func(ast)

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
