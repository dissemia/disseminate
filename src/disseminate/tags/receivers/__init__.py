"""
The receivers for tag events.
"""
from .hash import process_hash
from .macros import process_macros
from .content import process_content
from .typography import process_typography
from .paragraphs import process_paragraphs

__all__ = ('process_hash', 'process_macros', 'process_content',
           'process_typography', 'process_paragraphs')
