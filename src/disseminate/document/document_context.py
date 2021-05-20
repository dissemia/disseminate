"""
The document context
"""
import weakref
from copy import deepcopy

from .exceptions import TargetNotFound
from ..context import BaseContext
from ..label_manager import LabelManager
from ..signals.signals import signal
from ..paths import SourcePath, TargetPath
from ..utils.string import str_to_list
from ..utils.list import flatten
from .. import settings


find_builder = signal('find_builder')


class DocumentContext(BaseContext):
    """A context dict used for documents objects.
    """

    __slots__ = ()

    #: Required entries in the document context dict to be a valid document
    #: context--as well as their matching type to be checked.
    validation_types = {
        'document': None,
        'environment': None,
        'src_filepath': SourcePath,
        'project_root': SourcePath,
        'target_root': TargetPath,
        'targets': set,
        'paths': list,
        'label_manager': LabelManager,
        'mtime': float,
        'doc_id': str,
        'process_context_tags': set,
        'process_paragraphs': set,
        'label_fmts': dict,
        'label_resets': dict,
        'inactive_tags': set,
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

        # The modification time is the last time a document was changed. This
        # should be different for each document and subdocument. Note that the
        # mtime entry is set by the document object itself so that it can tell
        # when the full context has been read in.
        'mtime',

        # Paths are not inherited since we do not want to use paths for
        # template directories from the parent if the parent's template is
        # different. Also, the paths may be relative to the parent document
        # and may be invalid for a subdocument in a subdirectory.
        'paths',

        # Do not inherit builders. Each document and context has its own
        'builders',

        #: The contents of the body (specified by body_attr) doesn't carry over
        #: because each body has its own body.
        settings.body_attr,
    }

    #: The keys for context entries that should not be removed when the
    #: context is cleared. These are typically for entries setup in the
    #: __init__ of the class.
    exclude_from_reset = {
        # The document that owns the context and its parent variables should
        # not be reset, since we do not want to have this document inherited
        # from the parent.
        'document',

        # The following manager objects should remain the same every time the
        # context is reset. They should persist for a project, and they are
        # defined by the root document and build environment.
        'label_manager',
        'environment',

        # Keep the same list for paths when resetting. Note that will place
        # the entry here to prevent the lists path from being reset by the
        # parent 'reset' method. However, this reset method properly resets the
        # entry in the paths list without creating a new list object.
        'paths'
    }

    # Replace the following mutable entries.
    # When a document or template specified these entries, their values
    # should not be appended to the parent_context values--they should be
    # replaced with the new values.
    replace = {
        'targets',
        'inactive_tags',
    }

    def __init__(self, document, *args, **kwargs):
        self.document = document

        if kwargs.get('parent_context') is None:
            kwargs['parent_context'] = deepcopy(settings.default_context)

        # Conduct the rest of the initializations, including the reset.
        super(DocumentContext, self).__init__(*args, **kwargs)

    def reset(self):
        super(DocumentContext, self).reset()
        # Make sure the following entries are present from the parent or
        # root context
        self.is_valid('environment', 'project_root', 'target_root')

        document = self['document']()
        src_filepath = document.src_filepath
        self['src_filepath'] = src_filepath

        # set the document id
        if self.get('doc_id', None) is None:
            self['doc_id'] = str(document.doc_id)
        else:
            self['doc_id'] = str(self['doc_id'])

        # set the document's mtime
        if src_filepath.exists():
            self['mtime'] = src_filepath.stat().st_mtime

        # The the root document, if it wasn't set already
        if self.get('root_document', None) is None:
            self['root_document'] = weakref.ref(document)
            self['is_root_document'] = True
        else:
            self['is_root_document'] = False

        # Initialize the managers, if this is the root (document) context
        if self.get('label_manager', None) is None:
            self['label_manager'] = LabelManager(root_context=self)

        # Set the document's level. This is based off of the parent context's
        # level
        self['level'] = self.get('level', 0) + 1

        # Prepare the paths entry
        paths = self.setdefault('paths', [])
        paths.clear()

        # Include the path for the src_filepath
        local_path = SourcePath(project_root=src_filepath.project_root,
                                subpath=src_filepath.subpath.parent)
        if local_path not in paths:
            paths.append(local_path)

        # Include the project_root path
        if self['project_root'] not in paths:
            paths.append(self['project_root'])

    @property
    def document(self):
        """The document that owns this context"""
        # Retrieve and de-reference the document
        doc_ref = self.get('document', None)
        return doc_ref() if isinstance(doc_ref, weakref.ref) else None

    @document.setter
    def document(self, value):
        # Create a weakref to the document
        self['document'] = weakref.ref(value)

    @property
    def root_document(self):
        """The root document for a project"""
        # Retrieve and de-reference the document
        doc_ref = self.get('root_document', None)
        return doc_ref() if isinstance(doc_ref, weakref.ref) else None

    @root_document.setter
    def root_document(self, value):
        # Create a weakref to the document
        self['root_document'] = weakref.ref(value)

    @property
    def is_root_document(self):
        return self.get('is_root_document', False)

    @property
    def targets(self):
        """Retrieve a list of targets from the 'targets' or 'target'
        entry of the document.

        Returns
        -------
        target_list : List[str]
            A list of targets specified in the context.
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
        target_list = (str_to_list(targets) if isinstance(targets, str) else
                       targets)

        if 'none' in target_list:
            return []

        # Remove empty entries
        target_list = list(filter(bool, target_list))

        # Add trailing period to extensions in target_list, and make sure
        # there are no duplicates
        return {t if t.startswith('.') else '.' + t for t in target_list}

    def target_filepath(self, target):
        """Return the target filepath for this document's target, given
        the target.

        The target filepaths are retrieved from the builders. Accordingly,
        these should already have been loaded in the context. Additionally,
        this function may return target_filepaths for targets not listed by
        the 'targets' property. This is because these targets may be
        intermediary targets stored in a cache directory.

        Parameters
        ----------
        target : str
            The target to search

        Returns
        -------
        target_filepath : :obj:`.paths.TargetPath`
            The filepath for the target file of the document.

        Raises
        ------
        TargetNotFound
            Raised if a target was requested but not found.
        """
        builders = find_builder.emit(context=self, target=target)

        # convert from list of lists to flat list
        builders = list(flatten(builders))

        if len(builders) == 0:
            msg = ("A target_filepath could not be found for the '{}' "
                   "document target")
            raise TargetNotFound(msg.format(target))
        builder = builders[0]
        return builder.outfilepath

    def target_filepaths(self):
        """Return all target filepaths for this document's targets

        The target filepaths are retrieved from the builders. Accordingly,
        these should already have been loaded in the context. Additionally,
        this function may return target_filepaths for targets not listed by
        the 'targets' property. This is because these targets may be
        intermediary targets stored in a cache directory.

        Returns
        -------
        targets : Dict[str, :obj:`.paths.TargetPath`]
            The targets dict. The strings are the targets and the values
            are the corresponding target_filepaths.
        """
        builders = find_builder.emit(context=self)

        # convert from list of lists to flat list
        builders = list(flatten(builders))

        # get the targetfilepaths
        target_filepaths = [builder.outfilepath for builder in builders]

        # Formulate the targets dict. Key names should include a period.
        # ex: '.pdf'
        return {p.suffix: p for p in target_filepaths}

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
