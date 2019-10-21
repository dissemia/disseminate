"""
Receiver for document load to reset the context and document
"""
from ..signals import document_onload, document_deleted


@document_onload.connect_via(order=100)
@document_deleted.connect_via(order=100)
def reset_document(document):
    """Reset the context and managers for a document on load."""
    # Reset the context
    document.context.reset()

    # Reset the dependency manager
    if 'dependency_manager' in document.context:
        dep = document.context['dependency_manager']
        dep.reset(src_filepath=document.src_filepath)

    # Reset the label manager
    if 'label_manager' in document.context:
        label_manager = document.context['label_manager']

        # Reset the labels for this document.
        label_manager.reset(context=document.context)

    return document
