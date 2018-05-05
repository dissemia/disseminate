"""
The manager for labels.
"""
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
    and a id (ex: inept_introduction').

    Labels are added with the :meth:`add_label` method. These labels are
    collected and are only available after the :meth:`register_label` method
    is executed. When registering labels, old labels that aren't reference
    anymore are remove.

    Attributes
    ----------
    labels : set
        A set of labels
    collected_labels : dict
        A dictionary organized by document src_filepath (key, str) and a list
        of labels collected by the :meth:`add_label`. Collected labels aren't
        registered and available for tags to use yet. The
        :meth:`register_labels` method transfers them to the labels attribute
        and sets their order.
    """

    labels = None
    collected_labels = None

    def __init__(self):
        self.labels = []
        self.collected_labels = dict()

    def add_label(self, document, tag=None, kind=None, id=None):
        """Add a label.

        The add_label function adds a new or existing label to the
        collected_labels. The register_labels (:meth:`register_labels`)
        method must be invoked to register all collected labels to the list
        of available labels (self.labels)

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

        # See if the label already exists
        existing_labels = [label for label in self.labels if label.id == id]

        if len(existing_labels) == 0 or id is None:
            # If label doesn't exist or it's a generic label (i.e. no id),
            # create it.

            # Add the label
            label = Label(document=document, tag=tag, kind=kind, id=id,
                          local_order=None,
                          global_order=None)
        else:
            # A label with a match id was found. Use that one and make sure
            # its document, tag and kind match those given by this function
            label = existing_labels[0]
            label.document = document
            label.tag = tag
            label.kind = kind
        collected_labels = self.collected_labels.setdefault(src_filepath, [])
        collected_labels.append(label)

        return None

    def register_labels(self):
        """Process collected labels and register them in the label_manager.

        Labels are added with the :meth:`add_label` method. These labels are
        collected and are only available after the :meth:`register_label` method
        is executed. When registering labels, old labels that aren't referenced
        anymore are remove.

        Additionally, this function does the following:

            1. Sets the local_number and global_number of the newly registered
               tags. The global_number is the number for a given kind in the
               project and the local_number is the number for a given kind in
               the document.
            2. For heading labels, like chapter, section and subsection, the
               local_order is reset after elements like a chapter or section
               are encountered.
            3. A weakref to the chapter label or section label is placed in
               labels under these headings.
        """
        # See if there are collected_labels. If there aren't then all labels
        # are registered, and there's nothing to do.
        if len(self.collected_labels.keys()) == 0:
            return 0

        # Remove any labels for documents that no longer exist
        invalid_labels = [l for l in self.labels if l.document is None]
        for invalid_label in invalid_labels:
            self.labels.remove(invalid_label)

        # Now organize the labels and transfer the collected labels
        # First, get a list of all the document src_filepaths organized in
        # document number order. The document's number may not be set at this
        # point, in which case the document.number property will return None.
        # In this case, give it a default order of 0.
        documents = [l.document for l in self.labels]
        documents += [l.document for lst in self.collected_labels.values()
                      for l in lst]
        documents = filter(bool, documents)  # Remove 'None' items
        documents_dict = {d.src_filepath: d.number or 0 for d in documents}
        src_filepaths = sorted(documents_dict.keys(),
                               key=lambda k: documents_dict[k])

        # Create a new list of registered labels
        new_labels = []
        updated_label_count = 0
        global_counter = dict()  # Keep track of global count

        for src_filepath in src_filepaths:
            local_counter = dict()  # Keep track of global count
            chapter_label = None
            section_label = None

            # If there are collected labels for the given src_filepath, use
            # those labels. Otherwise, use those that are already registered
            if src_filepath not in self.collected_labels:

                # Use the existing registered label
                labels = [l for l in self.labels
                          if l.document.src_filepath == src_filepath]
            else:
                # Use the collected labels
                labels = self.collected_labels[src_filepath]
                updated_label_count += len(labels)

            # Process each label. Set the local_order and global_order count
            # for each label, set the corresponding chapter and section labels,
            # and add it to the new list of registered labels
            for label in labels:
                if label.kind:
                    if label.kind[-1] == 'chapter':
                        chapter_label = label

                        # Reset the local_counter for sections, subsections
                        local_counter['section'] = 0
                        local_counter['subsection'] = 0
                        local_counter['subsubsection'] = 0

                    elif label.kind[-1] == 'section':
                        section_label = label

                        # Reset the local_counter for sections, subsections
                        local_counter['subsection'] = 0
                        local_counter['subsubsection'] = 0

                    elif label.kind[-1] == 'subsection':
                        # Reset the local_counter for sections, subsections
                        local_counter['subsubsection'] = 0

                # Get the count for each of the kind items
                local_order, global_order = [], []
                for item in label.kind:
                    local_count = local_counter.setdefault(item, 0) + 1
                    global_count = global_counter.setdefault(item, 0) + 1

                    local_counter[item] = local_count
                    global_counter[item] = global_count

                    local_order.append(local_count)
                    global_order.append(global_count)

                label.chapter_label = chapter_label
                label.section_label = section_label
                label.local_order = tuple(local_order)
                label.global_order = tuple(global_order)

                new_labels.append(label)

            # Remove the collected labels
            if src_filepath in self.collected_labels:
                del self.collected_labels[src_filepath]

        # Move the new_labels to the registered labels
        self.labels.clear()
        self.labels += new_labels

        return updated_label_count

    def reset(self, document):
        """Reset the registration for the labels of the given document."""
        src_filepath = document.src_filepath
        self.collected_labels[src_filepath] = []

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
        existing_labels = {i for i in self.labels if i.id == id and
                           i.document is not None}

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
                                      if l.document is not None and
                                      l.document == document],
                                     key=lambda l: (l.document_number,
                                                    l.global_order))
        else:
            document_labels = sorted([l for l in self.labels
                                      if l.document is not None],
                                     key=lambda l: (l.document_number,
                                                    l.global_order))

        if kinds is None:
            return list(document_labels)

        # Filter labels by kind
        if isinstance(kinds, str):
            kinds = [kinds]

        returned_labels = []
        for kind in kinds:
            returned_labels += [l for l in document_labels if kind in l.kind]

        return returned_labels
