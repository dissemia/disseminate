"""
A manager for labels from headings, figures, equations, tables and other
document components.

Responsibilities
----------------

The labels and label manager are responsible for:

1. *Numbering*. Accurate and consistent formatting of labels and their
   identifer. *e.g.* Fig. 1.
2. *Internal links*. Work in conjunction with the ``@ref`` to correctly link
   to these elements.
3. *Tracking modification times*. Keep track of the modification times for
   the label so that references to those labels can trigger a document
   rendering.
"""
from . import receivers
from .types import ContentLabel, DocumentLabel
from .exceptions import LabelNotFound
from .label_manager import LabelManager

__all__ = ('receivers', 'ContentLabel', 'DocumentLabel', 'LabelNotFound',
           'LabelManager')
