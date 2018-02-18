"""
Tags for note environments.
"""
from .core import Tag


class Sidenote(Tag):
    """A sidenote tag."""

    aliases = ('marginnote', 'marginfig', 'sidefig')

    html_name = 'sidenote'
    tex_name = 'marginnote'

    active = True
