import os.path

from lxml.builder import E

from .. import settings


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
    """A label used for referencing

    Parameters
    ----------
    document : :obj:`disseminate.Document`
        The document (:obj:`disseminate.Document`) that owns this label.
    kind : str
        The kind of the label. ex: 'figure', 'chapter', 'equation'
    id : str
        The (unique) identifier of the label. ex: 'nmr_introduction'.
    contents : str, optional
        The short description for the label that can be used in the reference.
    local_number : int
        The number of the label in the current document.
    global_number : int
        The number of the label in the project.
    """
    __slots__ = ('document', 'kind', 'id', 'contents',
                 'local_number', 'global_number')

    def __init__(self, document, kind, id, contents=None,
                 local_number=None, global_number=None):
        self.document = document
        self.kind = kind
        self.id = id
        self.contents = contents
        self.local_number = local_number
        self.global_number = global_number

    def __repr__(self):
        return "({} {}-{})".format(self.id, self.local_number,
                                   self.global_number)

    @property
    def src_filepath(self):
        """The src_filepath of the document which owns this label."""
        assert (self.document is None and not
                hasattr(self.document, 'src_filepath'),
                "A document must own the label '{}'".format(self))
        return self.document.src_filepath

    def short(self, local_context=None, global_context=None):
        """The short text for the label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.

        Returns
        -------
        short_description : str
            The short description for this label. ex: Fig. 1
        """
        # Get the format string for the short label
        if isinstance(local_context, dict) and self.kind in local_context:
            text = local_context[self.kind]
        elif isinstance(global_context, dict) and self.kind in global_context:
            text = global_context[self.kind]
        elif self.kind in settings.label_format:
            text = settings.label_format[self.kind]
        else:
            text = self.kind

        # Get the document's number
        if (isinstance(local_context, dict) and
           'document_number' in local_context):
            document_number = (local_context['document_number'] if
                               'document_number' in local_context else '')
        else:
            document_number = ''

        # Format the text
        text = text.format(number=self.local_number,
                           document_number=document_number)

        return text

    def label(self, local_context=None, global_context=None):
        """The text label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.

        Returns
        -------
        label : str
            The text label
        """
        return self.short(local_context, global_context) + settings.label_sep

    def label_html(self, local_context=None, global_context=None):
        """The html label (anchor).

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.

        Returns
        -------
        html_entity : :obj:`lxml.builder.E`
            A 'span' element with the 'id' set to this label's identifier.
        """
        text = self.label(local_context, global_context)
        attrs = {'class': self.kind + '-label',
                 'id': self.id}
        return E('span', text, **attrs)

    def ref_html(self, local_context=None, global_context=None):
        """An html reference link to this label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.

        Returns
        -------
        html_entity : :obj:`lxml.builder.E`
            A 'a' element with the 'href' set to this label's identifier.
            By default, the short decription is used.
        """
        # Construct the anchor, if an id has been specified
        anchor = '#' + self.id if isinstance(self.id, str) else ''

        # Cunstrum the link
        # See if it's on a different document from the src_filepath
        if (isinstance(local_context, dict) and
           '_src_filepath' in local_context and
           local_context['_src_filepath'] == self.src_filepath):
            # the documents match, make an internal link

            link = anchor
        else:
            # the documents do not match, make a link to a different page

            location_file = self.document.target_filepath(target='.html',
                                                          render_path=False)
            link = location_file + anchor

        text = self.short(local_context, global_context)

        if link != "":
            return E('a', text, href=link)
        else:
            return text

    def ref_tex(self, local_context=None, global_context=None):
        """An tex reference to this label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.

        Returns
        -------
        html_entity : :obj:`lxml.builder.E`
            A 'a' element with the 'href' set to this label's identifier.
            By default, the short decription is used.
        """
        return self.short(local_context, global_context)


class LabelManager(object):
    """Manage labels and references.

    Manages labels for a project. Labels have a kind (ex: 'figure', 'chapter')
    and a id (ex: inept_introduction'). Names are expected to be unique
    between all documents of a project.

    Attributes
    ----------
    labels : set
        A set of labels
    _counters : dict
        The kind's count, starting from 1.
        - key: a tuple of str (src_filepath, kind) or a str (kind). The former
          is used for local counters within a document, and the latter is used
          for global counters within a project.
        - value: the count (int)
    """

    labels = None

    def __init__(self):
        self.labels = set()

    def add_label(self, document, kind, id=None, contents=None):
        """Add a label.

        Parameters
        ----------
        document : :obj:`disseminate.Document`
            The document (:obj:`disseminate.Document`) that owns this label.
        kind : str
            The kind of the label. ex: 'figure', 'chapter', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.
        contents : str, optional
            The short description for the label that can be used as the
            reference.

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
        src_filepath = document.src_filepath

        # Check to see if a label is unique for a project. A generic label id
        # (i.e. None) is guaranteed to be unique
        if id is not None:
            existing_labels = {i for i in self.labels if i.id == id}

            if existing_labels:
                label = existing_labels.pop()
                msg = "The label '{}' was already defined by the document {}."
                raise DuplicateLabel(msg.format(label.name,
                                                label.document.src_filepath))

        # Get the local_number and global_number of this label, based on
        # current counts
        kind_labels = {i for i in self.labels if i.kind == kind}
        global_number = len(kind_labels) + 1
        local_number = len([i for i in kind_labels
                            if i.src_filepath == src_filepath]) + 1

        # Add the label
        label = Label(document=document, kind=kind, id=id, contents=contents,
                      local_number=local_number, global_number=global_number)
        self.labels.add(label)

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
        """Return a filtered list of all labels for the given document.

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
        # Filter labels by document
        if document is not None:
            returned_labels = sorted([l for l in self.labels
                                      if l.document == document],
                                     key=lambda x: x.global_number)
        else:
            returned_labels = sorted([l for l in self.labels],
                                     key=lambda x: x.global_number)

        if kinds is None:
            return list(returned_labels)

        # Filter labels by kind
        if isinstance(kinds, str):
            kinds = [kinds]

        return [l for l in returned_labels if l.kind in kinds]

    def reset(self, document=None):
        """Reset the labels tracked by the LabelManager.

        Parameters
        ----------
        document : document, str or None
            - If a document (:obj:`disseminate.Document`) is specified, remove
              all labels for this document.
            - If not specified (None), all dependencies are removed.
        """
        if document is not None:
            # Go through all labels
            labels_to_remove = set()
            for label in self.labels:
                # Find the labels that match the document_src_filepath
                if label.document == document:
                    labels_to_remove.add(label)

            # Remove the labels
            self.labels -= labels_to_remove
        else:
            self.labels.clear()

        # Reset the numbers for the labels, which are counted by kind
        kinds = {i.kind for i in self.labels}
        for kind in kinds:
            kind_labels = sorted([i for i in self.labels if i.kind == kind],
                                 key=lambda x: x.global_number)

            # Set the global_number and local_number
            local_numbers = dict()
            for number, label in enumerate(kind_labels, 1):
                label.global_number = number

                sf = label.document.src_filepath
                local_numbers[sf] = local_numbers.setdefault(sf, 0) + 1

                label.local_number = local_numbers[sf]
