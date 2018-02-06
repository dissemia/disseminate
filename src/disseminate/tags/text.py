"""
Text formatting tags
"""
from .core import Tag, TagError

from lxml.etree import Entity


class Bold(Tag):
    """A bold tag."""
    aliases = ("b", "textbf", "strong")
    html_name = "strong"
    tex_name = "textbf"


class Italics(Tag):
    """An italics tag."""
    aliases = ("i", "textit")
    html_name = "i"
    tex_name = "textit"


class Sup(Tag):
    """A superscript tag."""
    html_name = "sup"

    def tex(self, level=1):
        # Collect the content elements
        if isinstance(self.content, list):
            elements = ''.join([i.tex(level + 1) if hasattr(i, 'tex') else i
                                for i in self.content])
        elif isinstance(self.content, str):
            elements = self.content
        else:
            elements = None

        return "\\ensuremath{^{" + elements + "}}"


class Sub(Tag):
    """A subscript tag."""
    html_name = "sub"

    def tex(self, level=1):
        # Collect the content elements
        if isinstance(self.content, list):
            elements = ''.join([i.tex(level + 1) if hasattr(i, 'tex') else i
                                for i in self.content])
        elif isinstance(self.content, str):
            elements = self.content
        else:
            elements = None

        return "\\ensuremath{_{" + elements + "}}"


class Greek(Tag):
    """One or more greek characters."""

    aliases = ("gr",)

    def assert_not_nested(self):
        """Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @greek tag cannot have tags nested within it."
            raise TagError(msg)

    def html(self, level=1):
        self.assert_not_nested()
        return Entity(self.content.strip())

    def tex(self, level=1):
        self.assert_not_nested()
        return "\\ensuremath{\\" + self.content + "}"