"""
The DocumentFactory for selecting the correct Document class and create
document objects.
"""
from .document import Document

class DocumentFactory(object):
    """A document factory for selecting the correct document class and create
    document objects."""

    def document(self, targets, *args, **kwargs):
        kwargs['targets'] = targets
        return Document(*args, **kwargs)