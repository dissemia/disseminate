"""
The DocumentFactory for selecting the correct Document class and create
document objects.
"""
from .document import Document
from .compiled_document import CompiledDocument
from .. import settings


class DocumentFactory(object):
    """A document factory for selecting the correct document class and create
    document objects."""

    def document(self, targets, *args, **kwargs):
        kwargs['targets'] = targets

        # Use a CompiledDocument if any of the targets are for compiled
        # documents
        if any(t in settings.compiled_exts for t in targets.keys()):
            return CompiledDocument(*args, **kwargs)
        else:
            return Document(*args, **kwargs)
