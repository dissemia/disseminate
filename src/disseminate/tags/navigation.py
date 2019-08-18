"""
Navigation tags
"""
from .tag import Tag
from .ref import Ref


def relative_doc_label(context, relative_position, target=None):
    """Find a document label relative to the specified context's document.

    Parameters
    ----------
    context : :obj:`.DocumentContext`
        The document context that owns this tag.
    relative_position : int
        The relative position of the document label to find.
        ex: -1 is the previous document
            0 is the current document
            1 is the next document
    target : Optional[str]
        If specified, only documents with the given target are included in
        the document list.

    Returns
    -------
    document_label : Union[None, :obj:`.label_manager.types.Label`]
        The relative document label, if found, or None, if the label could not
        be found.
    """
    assert context.is_valid('doc_id', 'label_manager')

    target = (target if target is None or target.startswith('.') else
              '.' + target)
    doc_id = context.get('doc_id')
    label_manager = context.get('label_manager')
    doc_labels = (label_manager.get_labels(kinds='document')
                  if label_manager is not None else [])

    # If a target was specified, filter the doc_labels list to documents
    # that support rendering to the given target.
    if target is not None:
        # Retrieve all the documents for the doc_labels. This is needed to
        # check whether the documents can render to the specified target
        root_document = context.root_document
        docs_by_id = (root_document.documents_by_id()
                      if hasattr(root_document, 'documents_by_id') else dict())

        # Now prune doc_labels by the documents that can render to target
        doc_labels = [label for label in doc_labels
                      if label.doc_id in docs_by_id and
                      target in docs_by_id[label.doc_id].target_list]

    # Find this document's label
    this_doc_index = [i for i, label in enumerate(doc_labels)
                      if label.doc_id == doc_id]
    this_doc_index = this_doc_index[0] if len(this_doc_index) > 0 else None

    # Find the next document's label
    other_doc_index = (this_doc_index + relative_position
                       if this_doc_index is not None else None)
    other_label = (doc_labels[other_doc_index]
                   if other_doc_index is not None and
                   len(doc_labels) > other_doc_index >= 0 else
                   None)

    return other_label


class Next(Ref):
    """Produces links to the next document.

    .. note:: As opposed to the parent Ref tag, if a label is not found,
              an empty string is returned by the target format functions.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, mathmode=False, level=1):
        # The next reference is designed for html only
        return ""

    def html_fmt(self, content=None, level=1):
        # Get the label_id for the next document
        next_label = relative_doc_label(context=self.context,
                                        relative_position=1,
                                        target='.html')

        if next_label is not None:
            self.label_id = next_label.id
            return super(Next, self).html_fmt(content=content, level=level)
        else:
            return ""


class Prev(Ref):
    """Produces links to the previous document.

    .. note:: As opposed to the parent Ref tag, if a label is not found,
              an empty string is returned by the target format functions.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, mathmode=False, level=1):
        # The next reference is designed for html only
        return ""

    def html_fmt(self, content=None, level=1):
        # Get the label_id for the next document
        prev_label = relative_doc_label(context=self.context,
                                        relative_position=-1,
                                        target='.html')

        if prev_label is not None:
            self.label_id = prev_label.id
            return super(Prev, self).html_fmt(content=content, level=level)
        else:
            return ""
