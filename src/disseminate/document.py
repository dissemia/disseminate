"""
Classes and functions for rendering documents.
"""
import os.path

from .ast import process_ast
from .tags import Tag


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

    Attributes
    ----------
    src_filepath : str, optional
        A filename for a document (markup source) file.
        Either the src_filepath of src attribute should be set when creating
        documents.
    src : str, optional
        A string to render.
        Either the src_filepath of src attribute should be set when creating
        documents.
    target : str
        The extension of the target type to use (ex: '.html')

    string_processors : list of str, **class attribute**
        A list of functions to process the string before conversion to the
        AST. These functions simply accept a string argument and are executed
        in sequence.
    """

    src_filepath = None
    target_filepath = None
    target = None

    string_processors = []
    ast_processors = []
    ast_post_processors = []

    def __init__(self, src_filepath, target_filepath):
        self.src_filepath = src_filepath
        self.target_filepath = target_filepath
        self.target = os.path.splitext(target_filepath)[-1]  # ex: '.html'

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

    def context(self):
        """

        Returns
        -------
        global_context, local_context : dict, dict
            A dict that is accessible from the root context (global) and a
            dict that is accessible from a local context.
        """
        return None, None

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

    def render(self, input, context=None, template=None):
        """Convert the input to a formatted string.

        Parameters
        ----------
        input: str
            A string or filename with text to convert.

        Returns
        -------
        formatted_str: str
            The lexed and parsed string.
        """
        # get global contexts
        # process_string
        # process_ast
        # validate_ast
        # get contexts from tags
        # postprocess_ast
        # render and save to output file

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