"""
Receiver for document load to reset the context and document
"""
from ..signals import document_onload, document_deleted


@document_onload.connect_via(order=100)
def reset_document(document, **kwargs):
    """Reset the context and managers for a document on load."""
    context = document.context or dict()

    # Reset the context
    context.reset()

    return document


@document_deleted.connect_via(order=100)
def delete_document(document, **kwargs):
    """Reset the context and managers for a document on document deletion."""
    context = document.context or dict()

    # Reset the context
    del context
    if document.context is not None:
        delattr(document, 'context')

    return document
