"""
Signals for label events
"""
from ..signals import signal


document_deleted = signal('document_deleted')


@document_deleted.connect_via(order=1000)
def deregister_labels(document):
    """A signal subscriber for removing labels when a document is deleted"""

    # Get the doc_id and label_manager for the document being destroyed
    context = document.context
    doc_id = context.get('doc_id')
    label_manager = context.get('label_manager')

    # Remove labels associated with the doc_id
    if doc_id is not None and label_manager is not None:
        labels_to_keep = [label for label in label_manager.labels
                          if label.doc_id != doc_id]

        # move the labels to keep back to the label_manager
        label_manager.labels.clear()
        label_manager.labels += labels_to_keep
