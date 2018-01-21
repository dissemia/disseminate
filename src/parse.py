import regex


# def parse_string(s):
#     """Parses a string into an AST comprising a list of lists with strings and
#     tags."""
#     return regex.sub(r'((?P<tag>@[A-Za-z]\w*)'
#                      r'{(?P<content>(?>[^{}@]+|(?R))*)})', parse_tag, s)
#
#
# def parse_tag(m):
#     """Process a tag regex match."""
#     content = parse_string(m.groupdict()['content'])
#     return [content, ]


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


def parse_ast(s):
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
        tag_content = parse_ast(m['content'])
        ast.append(Tag(tag_type, tag_content))

    # Add the end of the string
    ast.append(s[current_pos:])

    return ast


class Parser(object):
    """A general class to parse text files."""

    parsers = None

    def __init__(self):
        self.parsers = [parse_ast, ]

test = """
This is my test document. It has multiple paragraphs.

Here is a new one with @b{bolded} text as an example.
@marginfig{
  @src{media/files}
  @caption{This is my @i{first} figure.}
  }


Here is a new paragraph.
"""

print(parse_ast(test))