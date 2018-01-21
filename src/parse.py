import regex
from pprint import pprint


class TagFactory(object):
    pass

class Tag(object):

    tag_type = None
    tag_content = None

    def __init__(self, tag_type, tag_content):
        self.tag_type = tag_type
        if isinstance(tag_content, list) and len(tag_content) == 1:
            self.tag_content = tag_content[0]
        else:
            self.tag_content = tag_content

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.tag_type,
                                              content=self.tag_content)


def process_ast(s):
    """Parses a string into an AST comprising a list of lists with strings and
    tags."""
    ast = []
    current_pos = 0
    for m in regex.finditer(r'(@(?P<tag>[A-Za-z]\w*)'
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
        ast.append(Tag(tag_type, tag_content))

    # Add the end of the string
    ast.append(s[current_pos:])

    return ast


class Processor(object):
    """A general class to parse text files."""

    processors = None

    def __init__(self):
        self.processors = [process_ast, ]

    def _preprocess(self):
        """The preprocess step comprises, effectively, the lexing and
        conversion of tags for a string."""
        return None

    def _process(self):
        """The process step comprises the parsing of tags."""
        return None

    def _postprocess(self):
        """The post-process step comprises any formatting needed for the final
        format."""

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

test = """
This is my test document. It has multiple paragraphs.

Here is a new one with @b{bolded} text as an example.
@marginfig{
  @src{media/files}
  @caption{This is my @i{first} figure.}
  }


Here is a new paragraph.
"""

pprint(process_ast(test))