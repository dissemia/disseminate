"""
Classes and functions for rendering documents.
"""
import os.path

import regex

#from attributes import parse_attributes
#from .ast import process_ast
from . import settings


class DocumentError(Exception): pass


class Document(object):
    """A document rendered from a source file or string.

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
    src = None
    target = None

    string_processors = []
    ast_processors = []
    ast_post_processors = []

    def __init__(self, src=None, filepath=None, target=settings.default_target):
        """Initialize a document from the given input.

        Parameters
        ----------
        input: str
            A filepath for a document (markup source) file or a string
            comprising markup source data.
        target: str, optional
            The target extension of the rendered document. (ex: '.html')
        """
        assert src is not None or filepath is not None

        self.src = src
        self.src_filepath = filepath
        self.target = target if target.startswith(".") else "." + target

    def process_string(self):
        "Process the string before conversion to the ast"
        pass

    def process_ast(self):
        pass

    def postprocess_ast(self):
        "Process the ast, after conversion from the string"
        # Run each tag's process_ast
        # post-process of ast (create new paragraphs,
        # cleanup newlines, prevent paragraphs before equations.)
        pass

    def validate_ast(self):
        return None

    def context(self):
        pass

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