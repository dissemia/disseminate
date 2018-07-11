"""
The document context
"""
import weakref

from ..context import BaseContext
from .. import settings


class DocumentContext(BaseContext):
    """A context dict used for documents objects."""

    #: The following are *required* entries in the document context dict to be
    #: a valid context--as well as their matching type.
    #: None types are not check for the type of object stored in that entry.
    validation_types = {
        'document': None,
        'src_filepath': str,
        'project_root': str,
        'target_root': str,
        'paths': list,
        'label_manager': None,
        'dependency_manager': None,
        'mtime': float}

    default_context = settings.default_context

    #: The following are context entries that should not be copied (inherited)
    #: from the parent context.
    do_not_inherit = {
        # A subdocument shouldn't have the same subdocument 'include' entries
        # as the parent. Otherwise, documents could be included multiple times
        # or they may not be found.
        'include',
        # Each document should have a unique title
        'title',
        # Each document should have its own short title
        'short',
        # The modification time is the last time a document was changed. This
        # should be different for each document and subdocument.
        'mtime',
        # Paths are not inherited since we do not want to use paths for template
        # directories from the parent if the parent's template is different.
        # However, if the subdocument and parent document share the same
        # template, the renderer will correctly populate the paths for each.
        'paths'}

    #: The following are context entries that should not be removed when the
    #: context is cleared.
    exclude_from_clear = {
        # A document and its subdocuments should use the same single label
        # manager
        'label_manager',
        # A document and its subdocuments should use the same single dependency
        # manager
        'dependency_manager',
        # A document and its subdocuments all have the same project root
        # directory
        'project_root',
        # A document and its subdocuments all have the same target_root. Note
        # that the final target directory will also include the name of the
        # target extension.
        'target_root',
        # There can only be one root document for a project of documents and
        # subdocuments.
        'root_document'}

    def __init__(self, document, *args, **kwargs):
        super(DocumentContext, self).__init__(*args, **kwargs)

        self['document'] = weakref.ref(document)
        self['src_filepath'] = document.src_filepath

        # Set the root document variables; these should only be set if this
        # is the context for the root document.
        if 'project_root' not in self:
            self['project_root'] = document.project_root
        if 'target_root' not in self:
            self['target_root'] = document.target_root
        if 'root_document' not in self:
            self['root_document'] = weakref.ref(self)

        paths = self.setdefault('paths', [])
        if self['project_root'] not in paths:
            paths.append(self['project_root'])

        # Make sure the managers are initialized
        # ex: document.label_manager, document.dependency_manager
        for attr in dir(document):
            if 'attr'.endswith('_manager'):
                getattr(document, attr)
