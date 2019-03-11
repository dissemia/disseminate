"""
Tags are interpreted text elements in a disseminate document that are converted
to other elements in the rendered document, like bold text, images, figures,
equations and tables.
"""

from .core import Tag, TagError
from .factory import TagFactory
from . import (headings, text, img, asy, notes, figs, caption, eqs, toc,
               preamble, collection, ref)
from ..utils.classes import all_subclasses
from .. import settings

# Populate the settings dict of tag classes
for scls in all_subclasses(Tag):
    # Tag must be active
    if not scls.active:
        continue

    # Collect the name and aliases (alternative names) for the tag
    aliases = (list(scls.aliases) if scls.aliases is not None else
               list())
    names = [scls.__name__.lower(), ] + aliases

    for name in names:
        # duplicate or overwritten tag names are not allowed
        assert name not in settings.tag_classes
        settings.tag_classes[name] = scls
