import regex
import html

from collections import OrderedDict

control_char = r'@'


class TagFactory(object):
    pass

class Tag(object):

    tag_type = None
    tag_content = None
    tag_attributes = None

    def __init__(self, tag_type, tag_content, tag_attributes):
        self.tag_type = tag_type
        self.tag_attributes = tag_attributes
        if isinstance(tag_content, list) and len(tag_content) == 1:
            self.tag_content = tag_content[0]
        else:
            self.tag_content = tag_content

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.tag_type,
                                              content=self.tag_content)

    def html(self):
        """The html string for the tag, if the output target is html."""
        esc = html.escape
        if isinstance(self.tag_content, list):
            return ("<{tag}>"
                    "{content}</{tag}>".format(tag=esc(self.tag_type),
                                               content=esc(self.tag_content)))
        else:
            return "<{tag} />".format(tag=esc(self.tag_type))

    def default(self):
        """The default string for the tag, if no other format matches."""
        return self.tag_content


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


re_attrs = regex.compile(r'((?P<key>\w+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|\w+))'
                         r'|(?P<position>\w+))')

def parse_attributes(s):
    """Parses an attribute string into an OrderedDict of attributes.

    Parameters
    ----------
    s: str
        Input string of attributes of the form: "key1 = value1 key2 = value2"

    Returns
    -------
    attrs: OrderedDict
        The attributes dict.

    Examples
    --------
    >>> parse_attributes("data=one red=two")
    [('data', 'one'), ('red', 'two')]
    >>> parse_attributes(" class='base bttnred' style= media red")
    [('class', 'base bttnred'), ('style', 'media'), 'red']
    >>> parse_attributes("class='base btn' skip")
    [('class', 'base btn'), 'skip']
    """
    attrs = []

    for m in re_attrs.finditer(s):
        d = m.groupdict()
        if d.get('key', None) and d.get('value', None):
            attrs.append((d['key'], d['value'].strip('"').strip("'")))
        elif d.get('position', None):
            attrs.append(d['position'].strip("'").strip('"'))

    return attrs
    # # Break string about '=' characters and strip spaces and single/double
    # # quotes
    # items = [i.strip().strip("'").strip('"') for i in s.split('=')]
    #
    # attrs = OrderedDict()
    #
    # # Go through each of the items. The key should be the last word of each
    # # item, starting from the second one
    # if len(items) > 1:
    #     # The first item is just a key
    #     key = items[0]
    #
    #     # subsequent items are values (for the preceeding key) and keys for the
    #     # next item.
    #     for count, item in enumerate(items[1:], 1):
    #         # break the item by whitespace into a list of strings. Strip single
    #         # and double quotes
    #         pieces = [i.strip("'").strip('"') for i in item.split()]
    #         if count + 1 == len(items):
    #             value = ' '.join(pieces)
    #         else:
    #             value = ' '.join(pieces[:-1])
    #
    #         attrs[key] = value
    #         key = pieces[-1]
    # return attrs


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
@marginfig[offset=-1.0em]{
  @img{media/files}
  @caption{This is my @i{first} figure.}
  }

This is a @13C variable, but this is an email address: justin@lorieau.com

Here is a new paragraph.
"""

l = process_ast(test)
for i in l:
    print(i)