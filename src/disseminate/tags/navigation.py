"""
Navigation tags
"""
from os.path import relpath

from .tag import Tag
from .ref import Ref
from ..formats import html_tag, tex_cmd


def relative_label(context, relative_position, kinds='heading',
                   target=None):
    """Find a label for a document relative to the document specified by the
    given context.

    Parameters
    ----------
    context : :obj:`.DocumentContext`
        The document context that owns this tag.
    relative_position : int
        The relative position of the document label to find.
        ex: -1 is the previous document
            0 is the current document
            1 is the next document
    kinds : Optional[Tuple[str], str]
        The kind(s) of label to retrieve. The first label of this kind will be
        retrieved.
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

    # Setup and format the parameters
    target = (target if target is None or target.startswith('.') else
              '.' + target)

    # Get a dict of the document ids. This dict should be ordered.
    root_document = context.root_document
    docs_by_id = (root_document.documents_by_id()
                  if hasattr(root_document, 'documents_by_id') else dict())

    # Filter by available target, if available, and order the doc_ids
    if target is not None:
        doc_ids = [doc_id for doc_id, doc in docs_by_id.items()
                   if target in doc.target_list]
    else:
        doc_ids = list(docs_by_id.keys())

    # Find the doc_id for the current document
    current_doc_id = context['doc_id']
    current_doc_index = [i for i, doc_id in enumerate(doc_ids)
                         if doc_id == current_doc_id]
    current_doc_index = (current_doc_index[0] if len(current_doc_index) > 0
                         else None)

    # Find the doc_id for the other, relative document
    other_doc_index = (current_doc_index + relative_position
                       if current_doc_index is not None else None)
    other_doc_id = (doc_ids[other_doc_index]
                    if other_doc_index is not None and
                    0 <= other_doc_index < len(doc_ids) else None)

    # Get the request label from the label_manager
    label_manager = context.get('label_manager')
    labels = (label_manager.get_labels(doc_id=other_doc_id, kinds=kinds)
              if other_doc_id is not None else [])

    # Return the top (first) label
    return labels[0] if len(labels) > 0 else None


class Next(Ref):
    """Produces links to the next document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    2. The following are tag attributes that are recognized:

    kind : str
        The kind of label to reference by this tag. By default, it's a
        heading.
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
        kind = self.attributes.get('kind', default='heading')

        # Get the label_id for the next document
        next_label = relative_label(context=self.context, relative_position=1,
                                    kinds=kind, target='.html')

        if next_label is not None:
            self.label_id = next_label.id
            return super(Next, self).html_fmt(content=content, level=level)
        else:
            return ""


class Prev(Ref):
    """Produces links to the previous document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    2. The following are tag attributes that are recognized:

    kind : str
        The kind of label to reference by this tag. By default, it's a
        heading.
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
        kind = self.attributes.get('kind', default='heading')

        # Get the label_id for the next document
        prev_label = relative_label(context=self.context, relative_position=-1,
                                    kinds=kind, target='.html')

        if prev_label is not None:
            self.label_id = prev_label.id
            return super(Prev, self).html_fmt(content=content, level=level)
        else:
            return ""


class Pdflink(Ref):
    """Produces a link to the pdf for this document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # The next reference is designed for html only
        return ""

    def html_fmt(self, content=None, attributes=None, level=1):
        context = self.context

        # Only works if the document that owns this tag will be rendered to
        # a pdf.
        if '.pdf' not in context.targets:
            return ""

        # Get the document that owns this context and reconstruct the link to
        # the pdf.
        document = context.document
        pdf_target_filepath = document.target_filepath('.pdf')
        html_target_filepath = document.target_filepath('.html')

        # Get the relative path do this html document
        relative_path = relpath(pdf_target_filepath ,html_target_filepath)

        attributes = attributes if attributes is not None else self.attributes
        attrs = attributes.copy()
        attrs['class'] = 'ref'
        attrs['href'] = relative_path

        # wrap content in 'a' tag
        return html_tag('a', attributes=attrs,
                        formatted_content='pdf',
                        level=level,
                        pretty_print=False)  # no line breaks
