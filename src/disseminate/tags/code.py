"""
Code formatting tags
"""
from pygments import highlight, lexers, formatters
from markupsafe import Markup

from .tag import Tag
from .utils import find_files, content_to_str
from ..utils.types import StringPositionalValue
from ..formats import html_tag, tex_verb


class Code(Tag):
    """A tag for displaying code.
    """

    active = True

    process_content = False  # Do not process the contents
    process_typography = False  # Do not process typography tags
    include_paragraphs = True  # Do not include paragraphs within

    html_name = 'code'

    def __init__(self, name, content, attributes, context):
        super().__init__(name, content, attributes, context)

        # Load files, if needed
        files = find_files(self.content, context)

        if len(files) > 0:
            new_content = "\n".join([file.read_text() for file in files])
            self.content = new_content

    @property
    def lexer(self):
        """Get the lexer for code highlighting."""
        # Get string positional values from the attributes for the kind of
        # code
        string_positionals = [k for k, v in self.attributes.items()
                              if v == StringPositionalValue]

        # See if a lexer is available
        for string_positional in string_positionals:
            # See if a lexer is available
            lexer_name = string_positional.title() + 'Lexer'

            if lexer_name in lexers.LEXERS:
                return lexers.get_lexer_by_name(string_positional)

        # Otherwise try to guess it from the code block contents
        return lexers.guess_lexer(self.content)

    def html_fmt(self, content=None, attributes=None, level=1):
        # Format contents
        content = self.content if content is None else content
        content = content_to_str(content=content)

        # Get the lexer for the code and formatter for html
        if self.paragraph_role == 'block':
            lexer = self.lexer
            cssclass = ('highlight' if self.paragraph_role is None else
                        'highlight ' + self.paragraph_role)
            formatter = formatters.HtmlFormatter(cssclass=cssclass)

            html = highlight(content, lexer, formatter)
            return html_tag('div', attributes='class="code"',
                            formatted_content=Markup(html), level=level)
        else:
            return html_tag('code', attributes=self.attributes,
                            formatted_content=content, level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Format contents
        content = self.content if content is None else content
        content = content_to_str(content=content)

        if self.paragraph_role == 'block':
            lexer = self.lexer
            return highlight(content, lexer, formatters.LatexFormatter())
        else:
            return tex_verb(content)
