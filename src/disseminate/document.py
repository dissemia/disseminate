"""
Classes and functions for rendering documents.
"""
import os
import os.path

from .ast import process_ast, conversions
from .tags import Tag
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
    target_filepath : str
        The path (relative to the project_root directory) for the formatted
        document.
    template : A template object

    Attributes
    ----------
    src_filepath : str
        A filename for a document (markup source) file. This file should exist.
    target_filepath : str
        A filename to save the rendered document.
    target : str
        The extension of the target type to use (ex: '.html')
    template : template obj, optional
        A template to use for the rendered document.
    local_context : dict
        The context with values for the current document. (local)
    global_context : dict
        The context with values for all documents in a project. (global)

    string_processors : list of functions, **class attribute**
        A list of functions to process the string before conversion to the
        AST. These functions are executed in sequence and simply accept a
        string argument and return a processed string.
    ast_processors : list of functions, **class attribute**
        A list of functions to process the AST. These functions are executed in
        sequence and simply accept a AST argument and return a processed AST.

    """

    src_filepath = None
    target_filepath = None
    target = None
    template = None
    local_context = None
    global_context = None

    string_processors = []
    ast_processors = []
    ast_post_processors = []

    def __init__(self, src_filepath, target_filepath,
                 template=None, global_context=None):
        self.src_filepath = src_filepath
        self.target_filepath = target_filepath
        self.target = os.path.splitext(target_filepath)[-1]  # ex: '.html'
        self.template = template
        self.local_context = dict()
        self.global_context = (global_context
                               if isinstance(global_context, dict) else dict())

        if self.target == "":  # can't be the empty string
            msg = "The document '{}' must have a valid extension."
            raise DocumentError(msg.format(src_filepath))

    def process_string(self, string, target, **kwargs):
        """Process the string before conversion to the AST.

        Parameters
        ----------
        string : str
            The pre-processed string in document (markup source) format to
            further process.
        **kwargs : dict
            Keyword arguments to pass to the string_processor functions.

        Returns
        -------
        processed_string : str
            The processed string.
        """
        processed_string = string
        for func in self.string_processors:
            processed_string = func(processed_string, target, **kwargs)
        return processed_string

    def process_ast(self, string):
        """Process a string into an Abstract Syntax Tree (AST).

        Parameters
        ----------
        string : str
            The string in document (markup source) format to convert into an
            AST.

        Returns
        -------
        ast: list of str and :obj:`disseminate.Tag` objects.
            The generated AST.
        """
        ast = process_ast(string)
        return ast

    def postprocess_ast(self, ast, target, context):
        """Post-process the ast with target-specific options.

        Parameters
        ----------
        ast: list of str and :obj:`disseminate.Tag` objects.
            The AST.
        target: str, optional
            The target extension of the rendered document. (ex: '.html')

        Returns
        -------
        ast: list of str and :obj:`disseminate.Tag` objects.
            The post-processed AST.
        """
        # Run each tag's process_ast
        # post-process of ast (create new paragraphs,
        # cleanup newlines, prevent paragraphs before equations.)
        ast = process_tag_ast(ast, target)
        return ast

    def render(self):
        """Convert the src_filepath to a rendered document at target_filepath.

        Parameters
        ----------
        input: str
            A string or filename with text to convert.

        Returns
        -------
        formatted_str: str
            The lexed and parsed string.
        """
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
                          global_context=self.global_context)

        # Run individual tag process functions

        # Run the AST processing functions
        for processor in self.ast_processors:
            ast = processor(ast)

        # postprocess_ast

        # render and save to output file
        convert_func = conversions.get(self.target, None)
        output_string = convert_func(ast)

        with open(self.target_filepath, 'w') as f:
            f.write(output_string)

        return True



"""
# Initialize documents
tree = Tree()
documents = tree.documents()

# get global contexts
context = tree.context()
for document in documents:
    context.update(document.context())

# render documents
for document in documents:
    document.render(format=None) # do not save to file.
"""