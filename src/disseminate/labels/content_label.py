from .labels import Label
from ..utils.classes import weakattr


class ContentLabel(Label):
    """A label for a labeling a grouping of content, like a heading (branch or
    chapter, section, subsection) or an item that should show up in a table of
    contents, like a figure caption.

    Attributes
    ----------
    document_label : :obj:`disseminate.labels.Label`
        The label object for the document that owns this label.
    branch_label : :obj:`disseminate.labels.Label` or None
        The label for the branch under which this label is under.
    section_label : :obj:`disseminate.labels.Label` or None
        The label for the section under which this label is under.
    subsection_label : :obj:`disseminate.labels.Label` or None
        The label for the subsection under which this label is under.
    subsubsection_label : :obj:`disseminate.labels.Label` or None
        The label for the subsubsection under which this label is under.
    """

    title = None

    document_label = weakattr()
    branch_label = weakattr()
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
    def branch_number(self):
        branch_label = self.branch_label
        return (branch_label.global_order[-1] if branch_label is not None
                else '')

    @property
    def branch_title(self):
        branch_label = self.branch_label
        return branch_label.title if branch_label is not None else ''

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
        """The string for the number for the branch, section, subsection and
        so on. i.e. Section 3.2.1."""
        # Get a tuple of the numbers, remove empty string items and None
        numbers = filter(bool, (self.branch_number,
                                self.section_number,
                                self.subsection_number,
                                self.subsubsection_number))

        # Convert the numbers to strings
        numbers = map(str, numbers)

        # Return a string with the numbers joined by a character.
        return '.'.join(numbers)


class HeadingLabel(ContentLabel):
    """A content label for a document heading."""
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
    branch_label = None
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
        if not isinstance(label, HeadingLabel) and doc_id != label.doc_id:
            local_counter = dict()
            doc_id = label.doc_id

        if label.kind[-1] == 'branch':
            # If it's a new branch (i.e. a chapter or document title)
            # Get its label and reset the counters for the heading
            # registered_labels below
            branch_label = label
            section_label = None
            subsection_label = None
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['section'] = 0
            local_counter['subsection'] = 0
            local_counter['subsubsection'] = 0

        elif label.kind[-1] == 'section':
            section_label = label
            subsection_label = None
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['subsection'] = 0
            local_counter['subsubsection'] = 0

        elif label.kind[-1] == 'subsection':
            subsection_label = label
            subsubsection_label = None

            # Reset the local_counter for sections, subsections
            local_counter['subsubsection'] = 0

        elif label.kind[-1] == 'subsubsection':
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
        label.branch_label = branch_label
        label.section_label = section_label
        label.subsection_label = subsection_label
        label.subsubsection_label = subsubsection_label
