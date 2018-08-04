"""
The document context
"""
import weakref

from ..context import BaseContext
from ..labels import LabelManager
from ..dependency_manager import DependencyManager
from ..paths import SourcePath, TargetPath
from .. import settings


class DocumentContext(BaseContext):
    """A context dict used for documents objects."""

    __slots__ = ()

    #: The following are *required* entries in the document context dict to be
    #: a valid context--as well as their matching type.
    #: None types are not check for the type of object stored in that entry.
    validation_types = {
        'document': None,
        'src_filepath': SourcePath,
        'project_root': SourcePath,
        'target_root': TargetPath,
        'paths': list,
        'label_manager': LabelManager,
        'dependency_manager': DependencyManager,
        'mtime': float}

    default_context = settings.default_context

    #: The following are context entries that should not be copied (inherited)
    #: from the parent context. They should be unique to each context.
    do_not_inherit = {
        # The document reference in a context should be for the document that
        # owns the context. Consequently, a new context should have a new
        # document and the parent's document should not be inherited.
        'document',
        # A subdocument shouldn't have the same subdocument 'include' entries
        # as the parent. Otherwise, documents could be included multiple times
        # or they may not be found.
        'include', 'includes',
        # Each document should have a unique title
        'title',
        # Each document should have its own short title
        'short',
        # The modification time is the last time a document was changed. This
        # should be different for each document and subdocument. Note that the
        # mtime entry is set by the document object itself so that it can tell
        # when the full context has been read in.
        'mtime',
        # Paths are not inherited since we do not want to use paths for template
        # directories from the parent if the parent's template is different.
        # Also, the paths may be relative to the parent document and may be
        # invalid for a subdocument in a subdirectory.
        # Not that if the subdocument and parent document share the same
        # template, the renderer will correctly populate the paths for each.
        'paths'}

    #: The following are context entries that should not be removed when the
    #: context is cleared. These are typically for entries setup in the
    #: __init__ of the class.
    exclude_from_reset = {
        # The document that owns the context should not be reset, since we do
        # not want to have this document inherited from the parent.
        'document',
        # The following manager objects should remain the same every time the
        # context is reset. They should persist for a project.
        'label_manager',
        'dependency_manager',
        # Keep the same list for paths when resetting. Note that will place
        # the entry here to prevent the lists path from being reset by the
        # parent 'reset' method. However, this reset method properly resets the
        # entry in the paths list without creating a new list object.
        'paths'
        }

    def __init__(self, document, *args, **kwargs):
        # Create a weakref of the document. A weakref is used because the
        # context does not own the document, and document references
        # could be in multiple '_parent_context' entries for subdocuments.
        kwargs['document'] = weakref.ref(document)

        # Conduct the rest of the initializations, including the reset.
        super(DocumentContext, self).__init__(*args, **kwargs)

    def reset(self):
        super(DocumentContext, self).reset()
        document = self['document']()
        self['src_filepath'] = document.src_filepath

        # Set the root document variables; these should only be set if this
        # is the context for the root document.
        if 'project_root' not in self:
            self['project_root'] = document.project_root
        if 'target_root' not in self:
            self['target_root'] = document.target_root
        if 'root_document' not in self:
            self['root_document'] = weakref.ref(document)

        # Initialize the managers
        if 'label_manager' not in self:
            self['label_manager'] = LabelManager()
        if 'dependency_manager' not in self:
            dep = DependencyManager(project_root=document.project_root,
                                    target_root=document.target_root)
            self['dependency_manager'] = dep

        # Set the document's level. This is based off of the parent context's
        # level
        self['level'] = self['_parent_context'].get('level', 0) + 1

        # Prepare the paths entry
        paths = self.setdefault('paths', [])
        paths.clear()
        if self['project_root'] not in paths:
            paths.append(self['project_root'])
