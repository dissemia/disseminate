import regex

#from attributes import parse_attributes
from .ast import process_ast


control_char = r'@'


class Processor(object):
    """A general class to parse text files."""

    processors = None

    def __init__(self):
        self.processors = [process_ast, ]

    def preprocess(self):
        """The preprocess step comprises, effectively, the lexing and
        conversion of tags for a string."""
        return None

    def process(self):
        """The process step comprises the parsing of tags."""
        return None

    def postprocess(self):
        """The post-process step comprises any formatting needed for the final
        format."""
        return None

    def validate_preprocess(self):
        return None

    def format(self, input):
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
