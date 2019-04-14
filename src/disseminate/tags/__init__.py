"""
Tags are interpreted text elements in a disseminate document that are converted
to other elements in the rendered document, like bold text, images, figures,
equations and tables.
"""

from .tag import Tag
from .factory import TagFactory
from .exceptions import TagError
from . import processors
from . import (headings, text, img, asy, notes, figs, caption, eqs, toc,
               preamble, collection, ref)
