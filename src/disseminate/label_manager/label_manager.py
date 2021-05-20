"""
The manager for labels.
"""
from collections import OrderedDict
from threading import Lock

from .types import ContentLabel, DocumentLabel
from .exceptions import LabelNotFound, DuplicateLabel
from .register_orders import register_orders
from .register_content_labels import register_content_labels
from ..utils.classes import weakattr
from ..utils.dict import find_entry
from ..utils.string import replace_macros
from .. import settings


def parse_id(id, context=None):
    """Parses a label's identifier into a doc_id and label_id.

    Parameters
    ----------
    id : str
        The unique identifier (within a project of documents) for the label.
        The id includes the label_id, and it might include the doc_id.
        ex:
        'test.dm::intro'. (See label_sep for details)
        'ch:nmr-introduction'
    context : :obj:`.DocumentContext`
        The document context.

    Returns
    -------
    doc_id, label_id : Tuple[Union[str, None], str]
        The doc_id and label_id from the label id.

    Examples
    --------
    >>> parse_id('intro')
    (None, 'intro')
    >>> parse_id('fig:diagram-1')
    (None, 'fig:diagram-1')
    >>> parse_id('test1.dm::fig:diagram-1')
    ('test1.dm', 'fig:diagram-1')
    """
    if context is not None and 'label_sep' in context:
        label_sep = context['label_sep']
    else:
        label_sep = settings.default_context['label_sep']

    parts = id.split(label_sep)
    return tuple(parts) if len(parts) == 2 else (None, parts[0])


class LabelManager(object):
    """Manage labels for a project (a document tree).

    Parameters
    ----------
    root_context : :obj:`DocumentContext <.DocumentContext>`
        The context for the root document. The label manager does not own the
        context object, so only a weak reference to the context is stored.

    Attributes
    ----------
    labels : Dict[Tuple[str,str], :obj:`Label <.label_manager.types.Label>`]
        A list of labels where the key is the (doc_id, label_id) and the values
        are the label objects.
    """

    root_context = weakattr()
    labels = None
    collected_labels = None
    registered = False

    def __init__(self, root_context):
        self.labels = OrderedDict()
        self.root_context = root_context

    def register(self, context=None):
        """Register the labels.
        """
        if self.registered:
            return None

        # Only 1 thread should register the labels at a time
        lock = Lock()
        lock.acquire(blocking=True, timeout=10)
        context = context or self.root_context

        # Run the registration functions.
        for func in (register_orders,  # Register label 'order' attribute
                     register_content_labels,  # Set chapter/section attributes
                     ):
            func(labels=self.labels, root_context=context)

        # Labels have been registered. Release the lock
        self.registered = True
        if lock.locked():
            lock.release()

    def reset(self, doc_ids=None):
        """Reset the the labels.

        Parameters
        ----------
        doc_ids : Union[str, List[str], Tuple[str]]
            If specified, remove the labels for the given doc_ids
        """
        # Prepare the parameters
        doc_ids = {doc_ids} if isinstance(doc_ids, str) else doc_ids

        if doc_ids is None:
            self.labels.clear()
        else:
            keys_to_remove = set(filter(lambda k: k[0] in doc_ids,
                                        self.labels.keys()))
            for key in keys_to_remove:
                del self.labels[key]

        self.registered = False

    def add_label(self, id, kind, context, label_cls, *args, **kwargs):
        """Add a label.

        Parameters
        ----------
        id : str
            The unique identifier (within a project of documents) for the
            label. The id includes the label_id and possibly the doc_id of
            the label. 'test.dm::intro'. (See parse_id for details)
            ex: 'ch:nmr-introduction'
        kind : Union[str, List[str], Tuple[str]]
            The kind of the label. ex: 'figure', ('heading', 'chapter'),
            'equation'
        context : :obj:`DocumentContext <.DocumentContext>`
            The context for the document adding the label. (This may be
            different from the context of the root document, self.root_context)
        label_cls : :class:`Type[Label] <.label_manager.types.Label>`
            The label class (or subclass) to use in creating the label.

        Raises
        ------
        DuplicateLabel : :exc:`DuplicateLabel <.DuplicateLabel>`
            Raised if a label with the same id already exists in this
            label manager.

        """
        self.registered = False

        # Parse the label_id
        doc_id, label_id = parse_id(id, context=context)
        if doc_id is None:
            assert context.is_valid('doc_id')
            doc_id = context['doc_id']

        # Make the key for the labels dict
        label_key = (doc_id, label_id)

        # See if it's a duplicate
        if label_key in self.labels:
            other_label = self.labels[label_key]
            msg = "Label id '{}' already exists in the labels as '{}'."
            raise DuplicateLabel(msg.format(id, other_label))

        # Organize the kind into a tuple, if needed
        if isinstance(kind, str):
            kind = (kind,)

        # Now create the label and add it to the labels
        label = label_cls(doc_id=doc_id, id=label_id, kind=kind, order=None,
                          *args, **kwargs)
        self.labels[label_key] = label

        return label

    def add_content_label(self, id, kind, title, context):
        """Add content label.

        See :meth:`add_label` for usage details.
        """
        label = self.add_label(id=id, kind=kind, context=context,
                               label_cls=ContentLabel, title=title)
        label.title = title
        return label

    def add_document_label(self, id, kind, title, context):
        """Add document label.

        See :meth:`add_label` for usage details.
        """
        label = self.add_label(id=id, kind=kind, context=context,
                               label_cls=DocumentLabel, title=title)
        label.title = title
        return label

    def get_label(self, id, register=True, context=None):
        """Return the label for the given label id.

        .. note:: This function registers the added labels.

        Parameters
        ----------
        id : str
            The unique identifier (within a project of documents) for the
            label. The id includes the label_id and possibly the doc_id of
            the label. 'test.dm::intro'. (See parse_id for details)
            ex: 'ch:nmr-introduction'
        register : Optional[bool]
            If True, labels will be registered before doing the search
        context : :obj:`DocumentContext <.DocumentContext>`
            The context for the document adding the label. (This may be
            different from the context of the root document, self.root_context)

        Returns
        -------
        label : :obj:`Type[Label] <.label_manager.types.Label>`
            The corresponding label.

        Raises
        ------
        LabelNotFound : :exc:`LabelNotFound <.exceptions.LabelNotFound>`
            A LabelNotFound exception is raised if a label with the given id
            could not be found.
        """
        # Register the labels
        self.register()

        # Parse the label_id
        doc_id, label_id = parse_id(id, context=context or self.root_context)

        # Try the label key
        if (doc_id, label_id) in self.labels:
            return self.labels[(doc_id, label_id)]

        # Try to find the first label with a matching label_id, if no
        # doc_id is specified
        if doc_id is None:
            try:
                return next(l for k, l in self.labels.items()
                            if k[1] == label_id)
            except StopIteration:
                pass

        # I give up! I can't find the label.
        msg = "Could not find a label with identifier '{}'"
        raise LabelNotFound(msg.format(id))

    def get_labels_by_id(self, ids, register=True, context=None):
        """Return the labels with the given (optional) doc_ids and label_ids.

        Parameters
        ----------
        ids : Union[str, Tuple[str]]
            The unique identifiers (within a project of documents) for the
            label. The id includes the label_id and possibly the doc_id of the
            label. 'test.dm::intro'. (See parse_id for details)
            ex: 'ch:nmr-introduction'
        register : Optional[bool]
            If True, labels will be registered before doing the search
        context : :obj:`DocumentContext <.DocumentContext>`
            The context for the document adding the label. (This may be
            different from the context of the root document, self.root_context)

        Returns
        -------
        labels : List[:obj:`Type[Label] <.label_manager.types.Label>`]
            A list of label objects.

        Raises
        ------
        LabelNotFound : :exc:`LabelNotFound <.exceptions.LabelNotFound>`
            A LabelNotFound exception is raised if a label with the given id
            could not be found.
        """
        # Prepare the parameters
        ids = (ids if any(isinstance(ids, t) for t in (list, tuple, set))
               else [ids])

        # Register the labels
        self.register()

        return list(map(lambda x:
                        self.get_label(x, register=False, context=context),
                    ids))

    def get_labels_by_kind(self, doc_id=None, kinds=None, register=True):
        """Return a filtered and sorted list of all labels for the given
        document and kinds.

        .. note:: This function registers the added labels.

        Parameters
        ----------
        doc_id : Optional[str]
            If specified, only label for the given document id will be
            returned. (This is used an alternative to the context.)
        kinds : Optional[Union[str, List[str], Tuple[str]]
            If None, all label kinds are returned.
            If string, all labels matching the kind string will be returned.
            If a list of strings is returned, all labels matching all the kinds
            listed will be returned.
        register : Optional[bool]
            If True, labels will be registered before doing the search

        Returns
        -------
        labels : List[:obj:`Type[Label] <.label_manager.types.Label>`]
            A list of label objects.
        """
        # Prepare the parameters
        kinds = kinds or []
        kinds = (kinds if isinstance(kinds, list) or isinstance(kinds, tuple)
                 else [kinds])

        # Register the labels
        self.register()

        # Filter labels by doc_id.
        labels = self.labels.values()
        if doc_id is not None:
            labels = [label for label in labels if label.doc_id == doc_id]

        # Filter labels by kind
        returned_labels = []
        if kinds:
            for kind in kinds:
                returned_labels += [label for label in labels
                                    if kind in label.kind]
        else:
            returned_labels = labels

        return returned_labels

    def format_string(self, id, *keys, target=None):
        """Retrieve the formatted label string for a label.

        Label format strings are intended to be replaced with the values of the
        label by  replace_macros (:func:`replace_macros
        <disseminate.macros.replace_macros>`).

        Parameters
        ----------
        id : str
            The label of the label ex: 'ch:nmr-introduction'
        keys : Optional[List[str], Tuple[str]]
            If specified, use the given keys to find entries in the format_str
            dict. (see :func:`find_entry <disseminate.utils.dict.find_entry>`)
        target : Optional[str]
            If specified, try finding format strings for the given target.
        """
        label = self.get_label(id=id)

        dicts = []
        if 'label_fmts' in self.root_context:
            dicts.append(self.root_context['label_fmts'])

        # Construct the parameters for find_entry
        target = (target[1:] if isinstance(target, str) and
                  target.startswith('.') else target)

        # Find the label format string
        if len(keys) > 0:
            fmt_string = find_entry(dicts, *keys, suffix=target)
        else:
            fmt_string = find_entry(dicts, *label.kind, suffix=target)

        return replace_macros(fmt_string, {'@label': label})
