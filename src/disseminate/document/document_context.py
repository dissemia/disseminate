"""
The document context
"""
import weakref
from copy import deepcopy

from ..context import BaseContext
from ..label_manager import LabelManager
from ..dependency_manager import DependencyManager
from ..paths import SourcePath, TargetPath
from .. import settings


class DocumentContext(BaseContext):
    """A context dict used for documents objects.
    """

    __slots__ = ()

    #: Required entries in the document context dict to be a valid document
    #: context--as well as their matching type to be checked.
    validation_types = {
        'document': None,
        'src_filepath': SourcePath,
        'project_root': SourcePath,
        'target_root': TargetPath,
        'paths': list,
        'label_manager': LabelManager,
        'dependency_manager': DependencyManager,
        'renderers': dict,
        'mtime': float,
        'doc_id': str,
        'process_context_tags': set,
        'process_paragraphs': set,
        'label_fmts': dict,
        'label_resets': dict,
    }

    #: The keys for context entries that should not be inherited
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

        #: The toc entry is constructed for each document, and it should be
        #: unique to the document
        'toc',

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

    #: The keys for context entries that should not be removed when the
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
        'renderers',

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
            dep = DependencyManager(root_context=self)
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

    @property
    def root_document(self):
        # Retrieve and de-reference the document
        doc_ref = self.get('root_document', None)
        return doc_ref() if isinstance(doc_ref, weakref.ref) else None

    @root_document.setter
    def root_document(self, value):
        # Create a weakref to the document
        self['root_document'] = weakref.ref(value)

    @property
    def targets(self):
        """Retrieve a list of targets from the 'targets' or 'target'
        entry of the document  context.

        Returns
        -------
        target_list : List[str]
            A list of targets specified in the context.

        Examples
        --------
        >>> DocumentContext(targets='html, pdf').targets
        ['.html', '.pdf']
        >>> DocumentContext(target='txt').targets
        ['.txt']
        >>> DocumentContext(target=' ').targets
        []
        >>> DocumentContext().targets
        []
        """
        # Get the targets from the context.
        # In the default context, this is set as the 'targets' entry, which
        # may be over-written by the user. However, a 'target' entry
        # could be
        # used as well (for convenience), and it should be checked first,
        # since
        # it overrides the default 'targets' entry.
        if 'target' in self:
            targets = self['target']
        elif 'targets' in self:
            targets = self['targets']
        else:
            targets = ''

        # Convert to a list, if needed
        target_list = (targets.split(',') if isinstance(targets, str) else
                       targets)

        if len(target_list) == 1:
            target_list = [t.strip() for t in target_list[0].split(" ")]
        else:
            target_list = [t.strip() for t in target_list]

        if 'none' in target_list:
            return []

        # Remove empty entries
        target_list = list(filter(bool, target_list))

        # Add trailing period to extensions in target_list
        return [t if t.startswith('.') else '.' + t for t in target_list]

    @property
    def includes(self):
        """Retrieve a list of included subdocument source paths from the
        'include' entry of the context.

        Returns
        -------
        include_list : List[:obj:`SourcePath <.paths.SourcePath>`]
            A list of the paths for the included subdocuments.
        """
        assert self.is_valid('src_filepath')

        # Retrieve the include entry
        if 'include' in self:
            includes = self['include']
        elif 'includes' in self:
            includes = self['includes']
        else:
            includes = None

        # Make sure it's properly formatted as a string for further processing
        if not isinstance(includes, str):
            return []

        # Get the included subdocument paths. Strip extra space on the ends of
        # entries on each line and remove empty entries.
        includes = [path.strip() for path in includes.split('\n')
                    if not path.isspace() and path != '']

        # Reconstruct the paths relative to the context's src_filepath.
        src_filepath = self['src_filepath']
        subpath = src_filepath.subpath.parent
        project_root = src_filepath.project_root

        includes = [SourcePath(project_root=project_root,
                               subpath=subpath / path)
                    for path in includes]
        return includes
