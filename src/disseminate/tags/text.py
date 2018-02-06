"""
Text formatting tags
"""
from .core import Tag


class Bold(Tag):
    """A bold tag."""
    aliases = ("b", "textbf", "strong")
    html_name = "strong"
    tex_name = "textbf"


class Italics(Tag):
    """An italics tag."""
    aliases = ("i", "textit")
    html_name = "it"
    tex_name = "textit"


