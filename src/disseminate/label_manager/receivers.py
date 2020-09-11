"""
Signals for label events
"""
from .label_manager import LabelManager
from ..signals import signal


document_onload = signal('document_onload')


@document_onload.connect_via(order=1050)
def reset_label_manager(context, **kwargs):
    """Reset the label manager in the context on document load.

    This should be done before the text of the document is loaded in the
    document object.
    """
    # If no label manager is loaded, then this is the root context. Create a
    # label manager
    label_manager = context.setdefault('label_manager',
                                       LabelManager(root_context=context))

    # Remove labels for this document, so that new labels can be populated
    doc_id = context.get('doc_id', None)
    if doc_id is not None:
        label_manager.reset(doc_ids=doc_id)
