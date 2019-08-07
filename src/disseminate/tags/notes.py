"""
Tags for note environments.
"""
from .tag import Tag


class Sidenote(Tag):
    """A sidenote tag."""

    aliases = ('marginnote',)

    html_name = 'sidenote'
    tex_cmd = 'marginnote'

    active = True
