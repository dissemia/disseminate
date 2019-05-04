"""
A manager for labels from headings, figures, equations, tables and other
document components.

The labels and label manager are responsible for:

1. *Numbering*. Accurate and consistent formatting of labels and their
   identifer. *e.g.* Fig. 1.
2. *Internal links*. Work in conjunction with the ``@ref`` to correctly link
   to these elements.
"""
from .labels import Label, LabelNotFound
from .content_label import ContentLabel, DocumentLabel
from .label_manager import LabelManager
