from itertools import chain


class LabelError(Exception):
    """An error was encountered while processing a label."""
    pass


class DuplicateLabel(LabelError):
    """A label that was already defined is defined again"""
    pass


class LabelNotFound(LabelError):
    """Could not find a reference to a label"""
    pass


class Label(object):
    """A label used for referencing.

    Labels keep track of modification times (mtimes) through the @trackmtimes
    class wrapper. Any *changes* to class attributes not listed in the
    'excludeattrs' parameter to @trackmtimes will update the mtime attribute
    with the time of the modification. The initial mtime should correspond to
    the modification time of the source document that created this label.

    The mtimes are tracked because updates to labels may require an
    update of a rendered document. For example, a project may have two
    documents, each owning a label. If the first document (and its label) is
    updated, and the second document depends on this label, then the second
    document should be re-rendered if the label has changed. However, if that
    label hasn't changed, then the second document should not be re-rendered.

    Parameters
    ----------
    doc_id : str
        The unique identifier (for documents within a label manager) for the
        document that owns the label.
    id : str
        The unique identifier(s) of the label. ex: 'nmr_introduction'. This
        should be unique for the entire project.
    kind : tuple of str
        The kind of the label is a tuple that identified the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'h1',)
    mtime : float or None
        The modification time of the source document that created this label,
        or the modification time for changes to the label.
    local_order : tuple of int or None
        The number of the label in the current document. Since the kind is a
        tuple, the local_order corresponds to the count for each kind.
        ex: for a kind ('heading', 'h2') could have a local_order of (3, 2)
        which would represent the 3rd 'heading' and 2nd 'h2' item for a
        document.
    global_order : tuple of int or None
        The number of the label in all labels for the label manager.
    """

    doc_id = None
    id = None
    kind = None
    local_order = None
    global_order = None

    def __init__(self, doc_id, id, kind, mtime, local_order=None,
                 global_order=None):
        self.doc_id = doc_id
        self.id = id
        self.mtime = mtime
        self.local_order = local_order
        self.global_order = global_order

        # Make sure the label.kind is a tuple
        self.kind = (kind,) if isinstance(kind, str) else kind

    def __repr__(self):
        name = self.id if self.id else ''
        return "({}: {} {})".format(self.kind, name, self.global_order)

    @property
    def number(self):
        """The (local) number for the label's kind."""
        return self.local_order[-1]

    @property
    def global_number(self):
        """The (global) number for the label's kind."""
        return self.global_order[-1]

    @property
    def mtime(self):
        return getattr(self, '_mtime', None)

    @mtime.setter
    def mtime(self, value):
        """An mtime setter to make sure the modification time only increases"""
        current_value = getattr(self, '_mtime', None)
        if (not isinstance(current_value, float) or
            (isinstance(value, float) and value > current_value)):
            setattr(self, '_mtime', value)


def find_duplicates(registered_labels, collected_labels, exclude_labels=None,
                    *args, **kwargs):
    """Find duplicates in the collected_labels with those of labels that are
    already registered.

    Parameters
    ----------
    registered_labels : list of :obj:`disseminate.labels.Label`
        The list of labels that have been vetted, processed and registered.
    collected_labels : dict of list of :obj:`disseminate.labels.Label`
        The new labels that have been added but not yet registered. These will
        be tested for labels with duplicate ids in the registered labels.
        The keys are doc_id strings and the values are lists of labels.
    exclude_labels : tuple of :class:`disseminate.labels.Label`
        Labels that match the specified classes will not be checked for
        duplicates.

    Raises
    ------
    DuplicateLabel
        Exception raised if a label in the collected_labels has an id that is
        already registered for another document (with a different doc_id).
    """
    # Create an empty tuple for exclude_kinds, if None is specified
    if exclude_labels is None:
        exclude_labels = tuple()
    elif not isinstance(exclude_labels, tuple):
        exclude_labels = (exclude_labels,)

    # First get a mapping of the registered label ids and their corresponding
    # doc_ids
    label_ids = {label.id: label.doc_id for label in registered_labels}

    # Go through the collected labels and see if there are labels with ids
    # that have already been assigned to other doc_ids--provided the label
    # doesn't have a kind listed in the exclude_kinds parameter.
    duplicated_ids = [label for label in chain(*collected_labels.values())
                      if label.id in label_ids and
                      label_ids[label.id] != label.doc_id and
                      not any(isinstance(label, cls) for cls in exclude_labels)]

    # Raise an exception if duplicate ids were found.
    if len(duplicated_ids) > 0:
        msg = ("Label identifiers should be unique for all documents in a "
               "project. The following label identifers are used in multiple "
               "documents: "
               "{}".format(", ".join([l.id for l in duplicated_ids])))
        raise DuplicateLabel(msg)


def transfer_labels(registered_labels, collected_labels,
                    doc_ids, *args, **kwargs):
    """Transfer collected labels to the labels registry list and reorder
    labels according to their corresponding document's order.

    Parameters
    ----------
    registered_labels : list of :obj:`disseminate.labels.Label`
        The list of labels that have been vetted, processed and registered.
    collected_labels : dict of list of :obj:`disseminate.labels.Label`
        The new labels that have been added but not yet registered. These will
        be tested for labels with duplicate ids in the registered labels.
        The keys are doc_id strings and the values are lists of labels.
    doc_ids : list of str
        An ordered list of the document identifiers.
    """
    # Recontruct the labels list from existing, registered labels and
    # collected labels. These should have the same order as the documents.

    # Create a dict of doc_ids and the order of the documents
    doc_id_orders = {count: doc_id for count, doc_id in enumerate(doc_ids)}

    # Organize the registered labels by doc_id
    registered_labels_dict = dict()
    for label in registered_labels:
        labels_list = registered_labels_dict.setdefault(label.doc_id, [])
        labels_list.append(label)

    # Create an updated, ordered list of registered labels
    new_labels = []

    for count, doc_id in sorted(doc_id_orders.items()):
        if doc_id in collected_labels:
            new_labels += collected_labels.pop(doc_id)
        elif doc_id in registered_labels_dict:
            new_labels += registered_labels_dict[doc_id]

    # Transfer the labels
    registered_labels.clear()
    registered_labels += new_labels


def order_labels(registered_labels, exclude_labels=None, *args, **kwargs):
    """Set the local_order (within a document) and global_order (between
    many documents) of registered_labels.

    Parameters
    ----------
    registered_labels : list of :obj:`disseminate.registered_labels.Label`
        The list of registered_labels that have been vetted, processed and
        registered.
    exclude_labels : tuple of :class:`disseminate.labels.Label`
        Labels that match the specified classes will not be ordered. Presumably
        they'll be ordered by another function.
    """
    # Create an empty tuple for exclude_kinds, if None is specified
    if exclude_labels is None:
        exclude_labels = tuple()
    elif not isinstance(exclude_labels, tuple):
        exclude_labels = (exclude_labels,)

    # Keep track of the global count (the count between multiple documents
    # in a document tree) and the local count (the count within a document)
    global_counter = dict()
    local_counter = dict()  # Keep track of local count

    # Keep track of the doc_id for the document of the last label
    doc_id = None

    # Process each label.
    for label in registered_labels:
        # Skip if the label has a kind that is in the excluded kinds
        if (label.kind is None or
           any(isinstance(label, cls) for cls in exclude_labels)):
            continue

        # If the doc_id has changed, then its a new document.
        # In this case, reset the local_counter
        if doc_id != label.doc_id:
            local_counter = dict()
            doc_id = label.doc_id

        # Get the count for each of the kind items
        local_order, global_order = [], []
        for item in label.kind:
            local_count = local_counter.setdefault(item, 0) + 1
            global_count = global_counter.setdefault(item, 0) + 1

            local_counter[item] = local_count
            global_counter[item] = global_count

            local_order.append(local_count)
            global_order.append(global_count)

        label.local_order = tuple(local_order)
        label.global_order = tuple(global_order)
