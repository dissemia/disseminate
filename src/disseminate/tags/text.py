"""
Text formatting tags
"""
from textwrap import wrap

from markupsafe import Markup
from lxml import etree
from lxml.etree import Entity
from lxml.builder import E

from .core import Tag, TagError
from ..attributes import set_attribute
from .. import settings


class P(Tag):
    """A Paragraph tag

    Attributes
    ----------
    active : bool, default: True
        This tag is active.
    include_paragraphs : bool, default: False
        The contents of this tag can be included in paragraphs.
    """
    active = True
    include_paragraphs = False

    def tex_fmt(self, level=1, mathmode=False, content=None):
        tex = super(P, self).tex_fmt(level, mathmode, content)

        # Rewrap the text
        # if settings.tex_paragraph_width > 0:
        #     tex = "\n".join(wrap(tex, settings.tex_paragraph_width))

        # Add newlines around headings
        return "\n" + tex + "\n"


class Bold(Tag):
    """A bold tag.

    Attributes
    ----------
    aliases : list of str, default: ("b", "textbf", "strong")
        A list of strs for other names a tag goes by
    html_name : str, default: "strong"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_name : str, default: "textbf"
        If specified, use this name when rendering the tag to tex. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    aliases = ("b", "textbf", "strong")
    html_name = "strong"
    tex_name = "textbf"
    active = True


class Italics(Tag):
    """An italics tag.

    Attributes
    ----------
    aliases : list of str, default: ("i", "textit")
        A list of strs for other names a tag goes by
    html_name : str, default: "i"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_name : str, default: "textit"
        If specified, use this name when rendering the tag to tex. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    aliases = ("i", "textit")
    html_name = "i"
    tex_name = "textit"
    active = True


class Sup(Tag):
    """A superscript tag.

    Attributes
    ----------
    html_name : str, default: "sup"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    html_name = "sup"
    active = True

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = ''.join([i.tex_fmt(level + 1, mathmode)
                                if hasattr(i, 'tex') else i
                                for i in self.content])
        elif isinstance(content, str):
            elements = content
        else:
            elements = None

        return ("\\ensuremath{^{" + elements + "}}" if not mathmode else
                "^{" + elements + "}")


class Sub(Tag):
    """A subscript tag.

    Attributes
    ----------
    html_name : str, default: "sub"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    html_name = "sub"
    active = True

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = ''.join([i.tex_fmt(level + 1, mathmode)
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

    Attributes
    ----------
    active : bool, default: True
        This tag is active.
    """
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

    def html_fmt(self, level=1, content=None):
        kwargs = {'class': 'supsub'}
        return E('span', self._sup, E('br'), self._sub, **kwargs)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        formatted = "^{" + self._sup + "}_{" + self._sub + "}"
        return ("\\ensuremath{" + formatted + "}"
                if not mathmode else formatted)


class Symbol(Tag):
    """One or more greek characters.

    Attributes
    ----------
    aliases : list of str, default: ("smb",)
        A list of strs for other names a tag goes by
    active : bool, default: True
        This tag is active.
    """

    aliases = ("smb ",)
    active = True

    def assert_not_nested(self):
        """Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @symbol tag cannot have tags nested within it."
            raise TagError(msg)

    def html_fmt(self, level=1, content=None):
        self.assert_not_nested()
        e = Entity(self.content.strip())
        if level == 1:
            s = (etree.tostring(e, pretty_print=settings.html_pretty)
                      .decode("utf-8"))
            return Markup(s)  # Mark string as safe, since it's escaped by lxml
        else:
            return e

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        self.assert_not_nested()
        content = "\\" + content
        return ("\\ensuremath{" + content + "}" if not mathmode else
                content)


class Verb(Tag):
    """A verbatim tag for displaying unformatted blocks of text.

    Attributes
    ----------
    aliases : list of str, default: ("v", "pre", "verbatim")
        A list of strs for other names a tag goes by
    html_name : str, default: "code"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    include_paragraphs : bool, default: False
        The contents of this tag cannot be included in paragraphs.
    """

    aliases = ("v", "pre", "verbatim")
    active = True
    include_paragraphs = False

    html_name = 'code'

    def html_fmt(self, level=1, content=None):
        if self.name == "verbatim":
            self.attributes = set_attribute(self.attributes, ('class', 'block'))
        return super(Verb, self).html_fmt(level=level+1, content=content)

    def tex_fmt(self, *args, **kwargs):
        if self.name == "verbatim":
            return ("\n\\begin{verbatim}\n" + self.default_fmt() +
                    "\\end{verbatim}\n")
        else:
            return "\\verb|" + self.default_fmt() + "|"
