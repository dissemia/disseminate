"""
Text formatting tags
"""
from textwrap import wrap

from lxml.etree import Entity
from lxml.builder import E

from .core import Tag, TagError
from ..attributes import set_attribute
from .. import settings


class P(Tag):
    """A Paragraph tag"""
    active = True
    include_paragraphs = False

    def tex(self, level=1, mathmode=False, content=None):
        tex = super(P, self).tex(level, mathmode, content)

        # Rewrap the text
        if settings.tex_paragraph_width > 0:
            tex = "\n".join(wrap(tex, settings.tex_paragraph_width))

        # Add newlines around headings
        return "\n" + tex + "\n"


class Bold(Tag):
    """A bold tag."""
    aliases = ("b", "textbf", "strong")
    html_name = "strong"
    tex_name = "textbf"
    active = True
    include_paragraphs = False


class Italics(Tag):
    """An italics tag."""
    aliases = ("i", "textit")
    html_name = "i"
    tex_name = "textit"
    active = True
    include_paragraphs = False


class Sup(Tag):
    """A superscript tag."""
    html_name = "sup"
    active = True
    include_paragraphs = False

    def tex(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = ''.join([i.tex(level + 1, mathmode)
                                if hasattr(i, 'tex') else i
                                for i in self.content])
        elif isinstance(content, str):
            elements = content
        else:
            elements = None

        return ("\\ensuremath{^{" + elements + "}}" if not mathmode else
                "^{" + elements + "}")


class Sub(Tag):
    """A subscript tag."""
    html_name = "sub"
    active = True
    include_paragraphs = False

    def tex(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = ''.join([i.tex(level + 1, mathmode)
                                if hasattr(i, 'tex') else i
                                for i in content])
        elif isinstance(content, str):
            elements = content
        else:
            elements = None

        return ("\\ensuremath{_{" + elements + "}}" if not mathmode else
                "_{" + elements + "}")


class Supsub(Tag):
    """A superscript/subscript tag, together, that displays them one on top of
    the other.

    The content of the tag consists of two elements separated by a '&&'
    character. ex: @supsub{superscript && subscript}
    """
    include_paragraphs = False
    active = True

    _sup = None
    _sub = None

    def __init__(self, *args, **kwargs):
        super(Supsub, self).__init__(*args, **kwargs)

        # Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @supsub tag cannot have tags nested within it."
            raise TagError(msg)

        # assert that the element separator, '&&', is in the contents
        if self.content.count('&&') != 1:
            msg = ("The @supsub tag must contain only one element '&&' element "
                   "separator. ex: @supsub{{superscript && subscript}}. The "
                   "tag given was: {}")
            raise TagError(msg.format(self))

        # Seperate the superscript and subscript
        sup, sub = self.content.split('&&')
        self._sup = sup.strip()
        self._sub = sub.strip()

    def html(self, level=1, content=None):
        kwargs = {'class': 'supsub'}
        return E('span', self._sup, E('br'), self._sub, **kwargs)

    def tex(self, level=1, mathmode=False, content=None):
        formatted = "^{" + self._sup + "}_{" + self._sub + "}"
        return ("\\ensuremath{" + formatted + "}"
                if not mathmode else formatted)


class Symbol(Tag):
    """One or more greek characters."""

    aliases = ("smb ",)
    active = True
    include_paragraphs = False

    def assert_not_nested(self):
        """Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @greek tag cannot have tags nested within it."
            raise TagError(msg)

    def html(self, level=1, content=None):
        self.assert_not_nested()
        return Entity(self.content.strip())

    def tex(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        self.assert_not_nested()
        content = "\\" + content
        return ("\\ensuremath{" + content + "}" if not mathmode else
                content)


class Verb(Tag):
    """A verbatim tag for displaying unformatted blocks of text."""

    aliases = ("v", "pre", "verbatim")
    active = True
    include_paragraphs = False

    html_name = 'code'

    def html(self, level=1, content=None):
        if self.name == "verbatim":
            self.attributes = set_attribute(self.attributes, ('class', 'block'))
        return super(Verb, self).html(level)

    def tex(self, *args, **kwargs):
        if self.name == "verbatim":
            return ("\n\\begin{verbatim}\n" + self.default() +
                    "\\end{verbatim}\n")
        else:
            return "\\verb|" + self.default() + "|"
