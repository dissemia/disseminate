from .label import Label
from ...utils.classes import weakattr


def get_label_number(label, default=''):
    """Get the number for the given label"""
    order = getattr(label, 'order', None)
    if isinstance(order, tuple) and len(order) > 0:
        return order[-1]
    else:
        return default


class ContentLabel(Label):
    """A label for content, like a heading (chapter, section, subsection) or
    an item that should show up in a table of contents, like a figure caption.

    Attributes
    ----------
    document_label : :obj:`DocumentLabel <.types.DocumentLabel>`
        The label object for the document that owns this label.
    chapter_label : Optional[:obj:`ContentLabel <.types.ContentLabel>`]
        The label for the chapter under which this label is under.
    section_label : Optional[:obj:`ContentLabel <.types.ContentLabel>`]
        The label for the section under which this label is under.
    subsection_label : Optional[:obj:`ContentLabel <.types.ContentLabel>`]
        The label for the subsection under which this label is under.
    subsubsection_label : Optional[:obj:`ContentLabel <.types.ContentLabel>`]
        The label for the subsubsection under which this label is under.
    """

    title = None

    document_label = weakattr()
    title_label = weakattr()
    part_label = weakattr()
    chapter_label = weakattr()
    section_label = weakattr()
    subsection_label = weakattr()
    subsubsection_label = weakattr()

    def __init__(self, doc_id, id, kind, title, order=None):
        super().__init__(doc_id=doc_id, id=id, kind=kind, order=order)
        self.title = title

    def __repr__(self):
        if self.title is not None:
            return super().__repr__(title=self.title)
        else:
            return super().__repr__()

    @property
    def part_number(self):
        """The number for the part to which this label belongs."""
        return get_label_number(self.part_label)

    @property
    def part_title(self):
        """The title for the part to which this label belongs."""
        return getattr(self.part_label, 'title', '')

    @property
    def chapter_number(self):
        """The number for the chapter to which this label belongs."""
        return get_label_number(self.chapter_label)

    @property
    def chapter_title(self):
        """The title for the chapter to which this label belongs."""
        return getattr(self.chapter_label, 'title', '')

    @property
    def section_number(self):
        """The number for the section to which this label belongs."""
        return get_label_number(self.section_label)

    @property
    def section_title(self):
        """The title for the section to which this label belongs."""
        return getattr(self.section_label, 'title', '')

    @property
    def subsection_number(self):
        """The number for the subsection to which this label belongs."""
        return get_label_number(self.subsection_label)

    @property
    def subsection_title(self):
        """The title for the subsection to which this label belongs."""
        return getattr(self.subsection_label, 'title', '')

    @property
    def subsubsection_number(self):
        """The number for the subsubsection to which this label belongs."""
        return get_label_number(self.subsubsection_label)

    @property
    def subsubsection_title(self):
        """The title for the subsubsection to which this label belongs."""
        return getattr(self.subsubsection_label, 'title', '')

    @property
    def tree_number(self):
        """The string for the number for the chapter, section, subsection and
        so on.

        e.g. Section 3.2.1."""
        # Get a tuple of the numbers, remove empty string items and None
        numbers = filter(bool, (self.part_number,
                                self.chapter_number,
                                self.section_number,
                                self.subsection_number,
                                self.subsubsection_number))

        # Convert the numbers to strings
        numbers = map(str, numbers)

        # Return a string with the numbers joined by a character.
        return '.'.join(numbers)
