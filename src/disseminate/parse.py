import regex

#from attributes import parse_attributes
from .tags import Tag


control_char = r'@'


def process_ast(s):
    """Parses a string into an AST comprising a list of lists with strings and
    tags."""
    ast = []
    current_pos = 0
    for m in regex.finditer(r'(@(?P<tag>[A-Za-z]\w*)'
                            r'(?P<attributes>\[[^\]]+\])?'
                            r'{(?P<content>(?>[^{}@]+|(?R))*)})', s):
        # Find the match's start and end positions in the string
        start, end = m.span()

        # Add string up to this match
        ast.append(s[current_pos:start])

        # Reset the current position to the end of this match
        current_pos = end

        # Parse the match's content
        d = m.groupdict()
        tag_type = m['tag']
        tag_content = process_ast(m['content'])
        tag_attributes = m['attributes']
        ast.append(Tag(tag_type, tag_content, tag_attributes))

    # Add the end of the string
    ast.append(s[current_pos:])

    return ast


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
