import regex

#from attributes import parse_attributes
from .ast import process_ast


class Document(object):
    """A general class to generate documents."""

    ast_postprocessors = None

    def __init__(self, input, template, context=None, target_format='d'):
        self.ast_postprocessors = []

    @property
    def input(self):
        pass

    def preprocess(self):
        """The preprocess step comprises, effectively, the lexing and
        conversion of tags for a string."""
        return None

    def process_string(self):
        "Process the string before conversion to the ast"
        pass

    def postprocess_ast(self):
        "Process the ast, after conversion from the string"
        # Run each tag's process_ast
        # post-process of ast (create new paragraphs,
        # cleanup newlines, prevent paragraphs before equations.)
        pass

    def validate_ast(self):
        return None

    def generate_context(self):
        pass

    def render(self, input, template, context=None, format='default'):
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