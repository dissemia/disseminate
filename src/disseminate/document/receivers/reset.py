"""
Receiver for document load to reset the context and document
"""
from ..signals import document_onload, document_deleted


@document_onload.connect_via(order=100)
def reset_document(document, **kwargs):
    """Reset the context and managers for a document on load."""
    context = getattr(document, 'context', dict())
    src_filepath = context.get('src_filepath', None)

    # Reset the dependency manager
    if 'dependency_manager' in context and src_filepath is not None:
        dep = context['dependency_manager']
        dep.reset(src_filepath=document.src_filepath)

    # Reset the label manager
    if 'label_manager' in context and src_filepath is not None:
        label_manager = context['label_manager']

        # Reset the labels for this document.
        label_manager.reset(context=context)

    # Reset the context
    context.reset()

    return document


@document_deleted.connect_via(order=100)
def delete_document(document, **kwargs):
    """Reset the context and managers for a document on load."""
    context = getattr(document, 'context', dict())
    src_filepath = context.get('src_filepath', None)

    # Reset the dependency manager
    if 'dependency_manager' in context and src_filepath is not None:
        dep = context['dependency_manager']
        dep.reset(src_filepath=document.src_filepath)

    # Reset the label manager
    if 'label_manager' in context and src_filepath is not None:
        label_manager = context['label_manager']

        # Reset the labels for this document.
        label_manager.reset(context=context)

    # Reset the context
    del context
    delattr(document, 'context')

    return document
