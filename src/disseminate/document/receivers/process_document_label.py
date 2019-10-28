"""
A receiver to set the document label.
"""
from ..signals import document_onload
from ...utils.string import slugify


@document_onload.connect_via(order=1100)
def process_document_label(context, **kwargs):
    """A context processor to set the document label in the label manager."""
    assert context.is_valid('label_manager', 'document', 'src_filepath')

    label_manager = context['label_manager']
    src_filepath = context['src_filepath']
    doc = context['document']()  # de-reference weakref

    subpath_str = str(src_filepath.subpath)

    # Get the level of the document
    level = context.get('level', 1)

    # Generate the label_id. ex: 'sub/file1.dm' becomes 'doc:sub-file1-dm'
    label_id = 'doc:' + slugify(subpath_str)

    # Set the label for this document
    kind = ('document', 'document-level-' + str(level))
    label_manager.add_document_label(id=label_id,
                                     kind=kind, title=doc.short,
                                     context=context)
