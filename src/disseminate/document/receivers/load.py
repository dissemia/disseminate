"""
A receiver to load the document's string in the document context
"""
from ..signals import document_onload
from ... import settings


@document_onload.connect_via(order=200)
def load_document(document, **kwargs):
    """Load the document text file into the document context."""
    # Load the string from the src_filepath,
    string = document.src_filepath.read_text()

    # Place the text of the string in the 'body' attribute of the
    # context (see settings.body_attr)
    body_attr = settings.body_attr
    document.context[body_attr] = string
    return document
