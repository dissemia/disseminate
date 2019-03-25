"""
The document context
"""
import weakref
from copy import deepcopy

from ..context import BaseContext
from ..labels import LabelManager
from ..dependency_manager import DependencyManager
from ..paths import SourcePath, TargetPath
from ..utils.dict import find_entry
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
        'mtime': float,
        'doc_id': str}

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

        # Each document should have its own short title
        'short',

        #: The doc_id is unique for each document
        'doc_id',

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
        'paths',

        #: The contents of the body (specified by body_attr) doesn't carry over
        #: because each body has its own body.
        settings.body_attr,
        }

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
        self.document = document

        if kwargs.get('parent_context') is None:
            kwargs['parent_context'] = deepcopy(settings.default_context)

        # Conduct the rest of the initializations, including the reset.
        super(DocumentContext, self).__init__(*args, **kwargs)

    def reset(self):
        super(DocumentContext, self).reset()

        document = self['document']()
        self['src_filepath'] = document.src_filepath

        # set the document id
        if self.get('doc_id', None) is None:
            self['doc_id'] = str(document.doc_id)
        else:
            self['doc_id'] = str(self['doc_id'])

        # set the document's mtime
        if document.src_filepath.exists():
            self['mtime'] = document.src_filepath.stat().st_mtime

        # Set the root document variables; these should only be set if this
        # is the context for the root document.
        if self.get('project_root', None) is None:
            self['project_root'] = document.project_root
        if self.get('target_root', None) is None:
            self['target_root'] = document.target_root
        if self.get('root_document', None) is None:
            self['root_document'] = weakref.ref(document)

        # Initialize the managers, if this is the root (document) context
        if self.get('label_manager', None) is None:
            self['label_manager'] = LabelManager(root_context=self)
        if self.get('dependency_manager', None) is None:
            dep = DependencyManager(project_root=document.project_root,
                                    target_root=document.target_root)
            self['dependency_manager'] = dep

        # Set the document's level. This is based off of the parent context's
        # level
        self['level'] = self.get('level', 0) + 1

        # Prepare the paths entry
        paths = self.setdefault('paths', [])
        paths.clear()
        if self['project_root'] not in paths:
            paths.append(self['project_root'])

    @property
    def document(self):
        # Retrieve and de-reference the document
        doc_ref = self.get('document', None)
        return doc_ref() if isinstance(doc_ref, weakref.ref) else None

    @document.setter
    def document(self, value):
        # Create a weakref to the document
        self['document'] = weakref.ref(value)

    def label_fmt(self, major, intermediate=None, target=None):
        """Retrieve the label format string for the keys specified by the
        major as well as intermediate classification and the target for the
        document rendered.

        Label format strings are intended to be replaced with the
        StringTemplate (:class:`disseminate.utils.string.StringTemplate`).

        Parameters
        ----------
        major : string or tuple of str
            The major classification for the label format string. This may be
            the name of the tag using the label format string. ex: 'ref'
        intermediate : string or tuple of str, optional
            The intermediate classification for the label format string. This
            may be the kind(s) of label. ex: ('caption', 'figure')
        target : str or tuple of str, optional
            The target for the rendered document. ex: '.html'
        """
        dicts = []
        if 'label_fmts' in self:
            dicts.append(self['label_fmts'])
        if 'label_fmts' in settings.default_context:
            dicts.append(settings.default_context['label_fmts'])

        # Construct the parameters for find_entry
        target = (target.strip('.') if isinstance(target, str) and
                  target.startswith('.') else target)

        return find_entry(dicts=dicts, major=major, intermediate=intermediate,
                          minor=target)
