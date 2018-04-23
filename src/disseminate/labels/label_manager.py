"""
The manager for labels.
"""
import time

from .labels import Label


class LabelError(Exception):
    """An error was encountered while processing a label."""
    pass


class DuplicateLabel(LabelError):
    """A label that was already defined is defined again"""
    pass


class LabelNotFound(LabelError):
    """Could not find a reference to a label"""
    pass


class LabelManager(object):
    """Manage labels and references.

    Manages labels for a project. Labels have a kind (ex: 'figure', 'chapter')
    and a id (ex: inept_introduction'). Names are expected to be unique
    between all documents of a project.

    Attributes
    ----------
    labels : set
        A set of labels
    _document_counters : dict
        The kind's count, starting from 1, for a given document.
        - key: a tuple of str (src_filepath, kind)
        - value: the count (int)
    _global_counter = dict
        The kind's count, starting from 1, for the project.
        - key: a tuple of str (src_filepath, kind)
        - value: the count (int)
    """

    labels = None
    _document_counters = None
    _global_counter = None
    _mtime = None

    def __init__(self):
        self.labels = set()
        self._document_counters = dict()
        self._global_counter = dict()
        self.set_mtime()

    def set_mtime(self):
        """Set the modification time for the label_manager"""
        self._mtime = time.time()

    def get_mtime(self):
        """Get the last modification time for the label_manager"""
        return self._mtime

    def add_label(self, document, tag=None, kind=None, id=None):
        """Add a label.

        Parameters
        ----------
        document : :obj:`disseminate.Document`
            The document that owns the label.
        tag : None or :obj:`disseminate.Tag`
            The tag that owns the label.
        kind : tuple or str
            The kind of the label. ex: 'figure', 'chapter', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.

        Returns
        -------
        label : :obj:`Label`
            A named tuple with the label's information.

        Raises
        ------
        DuplicateLabel
            Raised if a label with the same id already exists in this
            label manager.

        """
        # Set up variables
        src_filepath = document.src_filepath

        # Organize the kind into a tuple, if needed
        if isinstance(kind, str):
            kind = (kind,)

        # Check to see if a label is unique for a project. A generic label id
        # (i.e. None) is guaranteed to be unique
        if id is not None:
            existing_labels = {i for i in self.labels if i.id == id}

            if existing_labels:
                label = existing_labels.pop()
                msg = "The label '{}' was already defined by the document {}."
                raise DuplicateLabel(msg.format(label,
                                                label.document.src_filepath))

        # Get the counter for this document
        counter = self._document_counters.setdefault(src_filepath, dict())
        global_counter = self._global_counter

        # Get the count for each of the kind items
        local_order, global_order = [], []
        for item in kind:
            count = counter.setdefault(item, 0) + 1
            global_count = global_counter.setdefault(item, 0) + 1

            counter[item] = count
            global_counter[item] = global_count

            local_order.append(count)
            global_order.append(global_count)

        # Add the label
        label = Label(document=document, tag=tag, kind=kind, id=id,
                      local_order=tuple(local_order),
                      global_order=tuple(global_order))
        self.labels.add(label)
        self.set_mtime()  # Update the modification time

        return label

    def get_label(self, id):
        """Return the label for the given label id.

        Parameters
        ----------
        id : str
            The label of the label ex: 'ch:nmr-introduction'

        Returns
        -------
        label : :obj:`Label`
            A named tuple with the label's information.

        Raises
        ------
        LabelNotFound
            A LabelNotFound exception is raised if a label with the given id
            could not be found.
        """
        # Find the label
        existing_labels = {i for i in self.labels if i.id == id}

        if len(existing_labels) == 0 or id is None:
            msg = "Could not find label '{}'"
            raise LabelNotFound(msg.format(id))

        return existing_labels.pop()

    def get_labels(self, document=None, kinds=None):
        """Return a filtered and sorted list of all labels for the given
        document.

        Parameters
        ----------
        document : :obj:`disseminate.Document` or None
            The document to search labels for.
            If None is specified, labels for all documents are returned.
        kinds : str or list of str or None
            If None, all label kinds are returned.
            If string, all labels matching the kind string will be returned.
            If a list of strings is returned, all labels matching all the kinds
            listed will be returned.

        Returns
        -------
        list of :obj:`disseminate.labels.Label`
            A list of label objects.
        """
        # Filter labels by document. Labels are sorted first by the order of a
        # document in a document tree, then by their global_order
        if document is not None:
            document_labels = sorted([l for l in self.labels
                                      if l.document == document],
                                     key=lambda x: (x.document.number or 0,
                                                    x.global_order))
        else:
            document_labels = sorted([l for l in self.labels],
                                     key=lambda x: (x.document.number or 0,
                                                    x.global_order))

        if kinds is None:
            return list(document_labels)

        # Filter labels by kind
        if isinstance(kinds, str):
            kinds = [kinds]

        returned_labels = []
        for kind in kinds:
            returned_labels += [l for l in document_labels if kind in l.kind]

        return returned_labels

    def reset(self, document=None, exclude_kinds=None):
        """Reset the labels tracked by the LabelManager.

        Parameters
        ----------
        document : document, str or None
            - If a document (:obj:`disseminate.Document`) is specified, remove
              all labels for this document.
            - If not specified (None), all dependencies are removed.
        exclude_kinds : str or tuple of string
            If specified, labels with this kind(s) are excluded from removal.
        """
        if isinstance(exclude_kinds, str):
            exclude_kinds = {exclude_kinds}
        elif exclude_kinds is not None:
            exclude_kinds = set(exclude_kinds)
        else:
            exclude_kinds = set()

        # Build a list of labels to remove
        labels_to_remove = set()

        # Go through the labels and determine whether they should be removed
        for label in self.labels:
            # Determine whether there are overlapping kinds between the label
            # and excluded_kinds
            matched_kinds = exclude_kinds & set(label.kind)

            if len(matched_kinds) != 0:  # An excluded kind matched
                continue

            # Remove the labelif the document is specified and matches the
            # label's document,
            if document is not None and label.document == document:
                labels_to_remove.add(label)
            elif document is None:
                labels_to_remove.add(label)

        # Remove the labels
        self.labels -= labels_to_remove

        # Reset the numbers for the labels, which are counted by kind
        self._document_counters.clear()
        self._global_counter.clear()

        # Labels are sorted first by the order of a document in a document tree,
        # then by their global_order
        for label in sorted(self.labels, key=lambda i: (i.document.number or 0,
                                                        i.global_order)):
            src_filepath = label.document.src_filepath
            counter = self._document_counters.setdefault(src_filepath, dict())
            global_counter = self._global_counter

            # Get the count for each of the kind items
            local_order, global_order = [], []
            for item in label.kind:
                count = counter.setdefault(item, 0) + 1
                global_count = global_counter.setdefault(item, 0) + 1

                counter[item] = count
                global_counter[item] = global_count

                local_order.append(count)
                global_order.append(global_count)

            label.local_order = tuple(local_order)
            label.global_order = tuple(global_order)

        # Reset the mtime
        self.set_mtime()
