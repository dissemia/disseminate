"""
Tags for figure environments.
"""

from .core import Tag


class Marginfig(Tag):

    html_name = 'marginfig'
    tex_name = 'marginfigure'
    active = True


class Caption(Tag):
    """A tag for captions."""

    html_name = 'caption'
    tex_name = 'caption'
    active = True
