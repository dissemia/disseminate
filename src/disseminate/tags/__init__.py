"""
Tags are interpreted text elements in a disseminate document that are converted
to other elements in the rendered document, like bold text, images, figures,
equations and tables.
"""

from .tag import Tag, TagFactory
from .exceptions import TagError
from . import signals, receivers
from . import (headings, text, img, asy, notes, figs, caption, code, eqs,
               featurebox, toc, list, preamble, label, ref, navigation, data,
               table)

__all__ = ('Tag', 'TagFactory', 'TagError', 'signals', 'receivers',
           'headings', 'text', 'img', 'asy', 'notes', 'figs', 'caption',
           'code', 'eqs', 'featurebox', 'toc', 'list', 'preamble', 'label',
           'ref', 'navigation', 'data', 'table')
