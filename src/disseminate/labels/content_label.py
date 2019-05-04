from .labels import Label
from ..utils.classes import weakattr


class ContentLabel(Label):
    """A label for a labeling a grouping of content, like a heading
    (chapter, section, subsection) or an item that should show up in a table of
    contents, like a figure caption.

    Attributes
    ----------
    document_label : :obj:`disseminate.labels.Label`
        The label object for the document that owns this label.
    chapter_label : :obj:`disseminate.labels.Label` or None
        The label for the chapter under which this label is under.
    section_label : :obj:`disseminate.labels.Label` or None
        The label for the section under which this label is under.
    subsection_label : :obj:`disseminate.labels.Label` or None
        The label for the subsection under which this label is under.
    subsubsection_label : :obj:`disseminate.labels.Label` or None
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

    def __init__(self, doc_id, id, kind, mtime, title,
                 local_order=None, global_order=None,):
        super(ContentLabel, self).__init__(doc_id=doc_id, id=id, kind=kind,
                                           mtime=mtime,
                                           local_order=local_order,
                                           global_order=global_order)
        self.title = title

    @property
    def document_number(self):
        document_label = self.document_label
        if document_label is not None:
            return document_label.global_count[0]
        return None

    @property
    def part_number(self):
        part_label = self.part_label
        return (part_label.global_order[-1] if part_label is not None
                else '')

    @property
    def part_title(self):
        part_label = self.part_label
        return part_label.title if part_label is not None else ''

    @property
    def chapter_number(self):
        chapter_label = self.chapter_label
        return (chapter_label.global_order[-1] if chapter_label is not None
                else '')

    @property
    def chapter_title(self):
        chapter_label = self.chapter_label
        return chapter_label.title if chapter_label is not None else ''

    @property
    def section_number(self):
        section_label = self.section_label
        return (section_label.local_order[-1] if section_label is not None
                else '')

    @property
    def section_title(self):
        section_label = self.section_label
        return section_label.title if section_label is not None else ''

    @property
    def subsection_number(self):
        subsection_label = self.subsection_label
        return (subsection_label.local_order[-1]
                if subsection_label is not None else '')

    @property
    def subsection_title(self):
        subsection_label = self.subsection_label
        return subsection_label.title if subsection_label is not None else ''

    @property
    def subsubsection_number(self):
        subsubsection_label = self.subsubsection_label
        return (subsubsection_label.local_order[-1] if subsubsection_label is
                                                       not None else '')

    @property
    def subsubsection_title(self):
        subsubsection_label = self.subsubsection_label
        return (subsubsection_label.title if subsubsection_label is not None
                else '')

    @property
    def tree_number(self):
        """The string for the number for the chapter, section, subsection and
        so on. i.e. Section 3.2.1."""
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


class DocumentLabel(ContentLabel):
    """A content label for a document heading--not a regular heading."""
    pass


def curate_content_labels(registered_labels, *args, **kwargs):
    """Curate content labels by setting the corresponding content labels above
    given content labels and set the order.

    The local_order is a bit different here, since it isn't reset between
    documents for heading labels.
    """

    # Keep track of the global count (the count between multiple documents
    # in a document tree) and the local count (the count within a document)
    global_counter = dict()
    local_counter = dict()  # Keep track of local count

    # Keep track of the current heading registered_labels
    part_label = None
    chapter_label = None
    section_label = None
    subsection_label = None
    subsubsection_label = None

    # Process each Contentlabel.
    content_labels = [label for label in registered_labels
                      if isinstance(label, ContentLabel)]

    # Keep track of the current doc_id
    doc_id = None

    for label in content_labels:
        # Switch the local count whenever a new document is encountered.
        # However, the local_counter is not reset between documents
        if not isinstance(label, DocumentLabel) and doc_id != label.doc_id:
            local_counter = dict()
            doc_id = label.doc_id

        if label.kind and label.kind[-1] == 'part':
            # If it's a new chapter (i.e. a chapter or document title)
            # Get its label and reset the counters for the heading
            # registered_labels below
            part_label = label
            chapter_label = None
            section_label = None
            subsection_label = None
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['chapter'] = 0
            local_counter['section'] = 0
            local_counter['subsection'] = 0
            local_counter['subsubsection'] = 0

        if label.kind and label.kind[-1] == 'chapter':
            # If it's a new chapter (i.e. a chapter or document title)
            # Get its label and reset the counters for the heading
            # registered_labels below
            chapter_label = label
            section_label = None
            subsection_label = None
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['section'] = 0
            local_counter['subsection'] = 0
            local_counter['subsubsection'] = 0

        elif label.kind and label.kind[-1] == 'section':
            section_label = label
            subsection_label = None
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['subsection'] = 0
            local_counter['subsubsection'] = 0

        elif label.kind and label.kind[-1] == 'subsection':
            subsection_label = label
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['subsubsection'] = 0

        elif label.kind and label.kind[-1] == 'subsubsection':
            subsubsection_label = label

        # Set the counters for headings
        # Get the count for each of the kind items
        local_order, global_order = [], []
        for item in label.kind:
            local_count = local_counter.setdefault(item, 0) + 1
            global_count = global_counter.setdefault(item, 0) + 1

            local_counter[item] = local_count
            global_counter[item] = global_count

            local_order.append(local_count)
            global_order.append(global_count)

        label.local_order = tuple(local_order)
        label.global_order = tuple(global_order)

        # Set the heading label for all registered_labels
        label.part_label = part_label
        label.chapter_label = chapter_label
        label.section_label = section_label
        label.subsection_label = subsection_label
        label.subsubsection_label = subsubsection_label
