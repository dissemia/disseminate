"""
Attributes are modifiers to tags that change *how* a tag is rendered.
Attributes are represented by ordered dicts that can validate their entries.
"""
from .attributes import Attributes, AttributeFormatError

__all__ = ('Attributes', 'AttributeFormatError')
