"""
A function to register content labels
"""
from .types import ContentLabel, DocumentLabel


def register_content_labels(labels, **kwargs):
    """Assign chapter/section/subsection links for Content labels.

    This processor only works on content labels (:obj:`ContentLabel
    <.types.ContentLabel>`)

    Parameters
    ----------
    labels : Dict[Tuple[str,str], :obj:`Label <.label_manager.types.Label>`]
        A list of labels where the key is the (doc_id, label_id) and the values
        are the label objects.
    """

    # Keep track of the current heading registered_labels
    part_label = None
    chapter_label = None
    section_label = None
    subsection_label = None
    subsubsection_label = None

    # Process each Contentlabel.
    content_labels = [label for label in labels.values()
                      if isinstance(label, ContentLabel)]

    # Keep track of the current doc_id
    doc_id = None

    for label in content_labels:
        # Switch the local count whenever a new document is encountered.
        # However, the local_counter is not reset between documents
        if not isinstance(label, DocumentLabel) and doc_id != label.doc_id:
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

        elif label.kind and label.kind[-1] == 'chapter':
            # If it's a new chapter (i.e. a chapter or document title)
            # Get its label and reset the counters for the heading
            # registered_labels below
            chapter_label = label
            section_label = None
            subsection_label = None
            subsubsection_label = None

        elif label.kind and label.kind[-1] == 'section':
            section_label = label
            subsection_label = None
            subsubsection_label = None

        elif label.kind and label.kind[-1] == 'subsection':
            subsection_label = label
            subsubsection_label = None

        elif label.kind and label.kind[-1] == 'subsubsection':
            subsubsection_label = label

        # Set the heading label for all registered_labels
        label.part_label = part_label
        label.chapter_label = chapter_label
        label.section_label = section_label
        label.subsection_label = subsection_label
        label.subsubsection_label = subsubsection_label
