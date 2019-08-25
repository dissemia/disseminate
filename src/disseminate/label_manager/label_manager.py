"""
The manager for labels.
"""
from .types import ContentLabel, DocumentLabel
from .exceptions import LabelNotFound
from .processors import ProcessLabels
from ..utils.classes import weakattr
from ..utils.dict import find_entry
from ..utils.string import replace_macros


class LabelManager(object):
    """Manage labels for a project (a document tree).

    Labels are added with the :meth:`add_label` methods. These labels are collected
    and are only available after the :meth:`register_labels` method is
    executed. Labels are automatically registered when the :meth:`get_label` and
    :meth:`get_labels` methods are used.

    The collection/register method is used because labels keep track of their
    modification times (mtimes) and update these if their parameters change. A
    change in the label's mtime indicates that a document needs to be
    re-rendered.

    Parameters
    ----------
    root_context : :obj:`DocumentContext <.DocumentContext>`
        The context for the root document. The label manager does not own the
        context object, so only a weak reference to the context is stored.

    Attributes
    ----------
    labels : List[:obj:`Label <.label_manager.types.Label>`]
        A list of registered labels
    collected_labels : Dict[str, List[:obj:`Label \
        <.label_manager.types.Label>`]]
        A dictionary organized by document src_filepath (key, str) and a list
        of labels collected by the :meth:`add_label` methods. Collected labels
        aren't registered and available for tags to use yet. The
        :meth:`register_labels` method transfers them to the labels attribute
        and sets their order.
    processors : List[:obj:`Type[ProcessLabel] \
        <.label_manager.processors.ProcessLabels>`]
        An ordered list of label processors executed on the collected and
        registered labels by the register_labels method.
    """

    root_context = weakattr()
    labels = None
    collected_labels = None

    processors = None

    def __init__(self, root_context):
        self.labels = []
        self.collected_labels = dict()
        self.root_context = root_context
        self.processors = ProcessLabels.processors(context=root_context)

    def add_label(self, id, kind, context, label_cls, *args, **kwargs):
        """Add a label.

        The add_label function adds a new or existing label to the
        collected_labels. The register_labels (:meth:`register_labels`)
        method must be invoked to register all collected labels to the list
        of available labels (self.labels)

        Typically, the helper methods, like :meth:`add_content_label` or
        :meth:`add_document_label` are used instead, as these specify the label
        class to use.

        Parameters
        ----------
        id : str
            The unique identifier (within a project of documents) for the label.
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
        assert context.is_valid('doc_id', 'mtime')

        # Get the values needed from the context
        doc_id = context['doc_id']
        mtime = context['mtime']

        # The objective here is to reuse labels, if possible, since this
        # produces an accurate mtime if the label is changed.

        # Organize the kind into a tuple, if needed
        if isinstance(kind, str):
            kind = (kind,)

        # First see if it's already been added to the collected labels.
        # If it has, simply return that.
        collected_labels = self.collected_labels.setdefault(doc_id, [])
        existing_collected_labels = [label for label in collected_labels
                                     if label.id == id]

        if len(existing_collected_labels) > 0:
            return existing_collected_labels[0]

        # Next, see if the label already exists in the registered labels.
        # If an existing label is found, we must transfer it to the
        # collected_labels.

        existing_labels = [label for label in self.labels if label.id == id]

        # Get the existing label, if found, and update it.
        label = None
        if len(existing_labels) > 0:
            label = existing_labels[0]
            label.kind = kind
            label.mtime = mtime  # update the mtime

        # If no matching label was found. Create a new one.
        if label is None:
            label = label_cls(doc_id=doc_id, id=id, kind=kind, mtime=mtime,
                              order=None, *args, **kwargs)

        collected_labels = self.collected_labels.setdefault(doc_id, [])
        collected_labels.append(label)

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

    def reset(self, context):
        """Reset the registration for the labels of the given document.

        Parameters
        ----------
        context : :obj:`DocumentContext <.DocumentContext>`
            The context for the document whose labels are being reset.
        """
        assert context.is_valid('doc_id')
        doc_id = context['doc_id']

        self.collected_labels[doc_id] = []

    def get_label(self, id):
        """Return the label for the given label id.

        .. note:: This function registers the added labels.

        Parameters
        ----------
        id : str
            The label of the label ex: 'ch:nmr-introduction'

        Returns
        -------
        label : :obj:`Type[Label] <.label_manager.types.Label>`
            A named tuple with the label's information.

        Raises
        ------
        LabelNotFound : :exc:`LabelNotFound <.exceptions.LabelNotFound>`
            A LabelNotFound exception is raised if a label with the given id
            could not be found.
        """
        # Make sure the labels are registered
        self.register_labels()

        # Find the label
        existing_labels = {i for i in self.labels if i.id == id}

        if len(existing_labels) == 0 or id is None:
            msg = "Could not find label '{}'"
            raise LabelNotFound(msg.format(id))

        return existing_labels.pop()

    def get_labels(self, doc_id=None, kinds=None):
        """Return a filtered and sorted list of all labels for the given
        document.

        .. note:: This function registers the added labels.

        Parameters
        ----------
        doc_id : Optional[str]
            If specified, only label for the given document id will be returned.
            (This is used an alternative to the context.
        kinds : Optional[Union[str, List[str], Tuple[str]]
            If None, all label kinds are returned.
            If string, all labels matching the kind string will be returned.
            If a list of strings is returned, all labels matching all the kinds
            listed will be returned.

        Returns
        -------
        labels : List[:obj:`Type[Label] <.label_manager.types.Label>`]
            A list of label objects.
        """
        # Make sure the labels are registered
        self.register_labels()

        # Filter labels by document.
        if doc_id is not None:
            document_labels = [l for l in self.labels if l.doc_id == doc_id]
        else:
            document_labels = self.labels

        if kinds is None:
            return list(document_labels)

        # Filter labels by kind
        if isinstance(kinds, str):
            kinds = [kinds]

        returned_labels = []
        for kind in kinds:
            returned_labels += [l for l in document_labels if kind in l.kind]

        return returned_labels

    def register_labels(self):
        """Process collected labels and register them in the label_manager.

        This function:

            1. Transfers the collected_labels to the list of registered labels
               (self.labels)
            2. Sets the local order (within a document) and global order
               (between multiple documents in a document tree) for labels.
            3. Sets references to the heading labels and the counts for
               heading labels.
        """
        # Only register labels if there are collected labels to register
        if len(self.collected_labels) > 0:
            for processor in self.processors:
                processor(registered_labels=self.labels,
                          collected_labels=self.collected_labels)

        return None

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
