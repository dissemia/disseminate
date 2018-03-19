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

# TODO: replace contents with the tag itself. How to communicate what kind of
# label or ref needed? short, caption?
# TODO: allow format strings to be parsed by ast
class Label(object):
    """A label used for referencing.

    Parameters
    ----------
    document : :obj:`disseminate.Document`
        The document (:obj:`disseminate.Document`) that owns this label.
    kind : tuple
        The kind of the label is a tuple that identified the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'h1',)
    id : str
        The (unique) identifier of the label. ex: 'nmr_introduction'.
    contents : str, optional
        The short description for the label that can be used in the reference.
    label_type : str, optional
        The label to show when constructing references for the label.
        options: 'short', 'caption'
    local_order : tuple of int
        The number of the label in the current document. Since the kind is a
        tuple, the local_order corresponds to the count for each kind.
        ex: for a kind ('heading', 'h2') could have a local_order of (3, 2)
        which would represent the 3rd 'heading' and 2nd 'h2' item for a
        document.
    global_order : tuple of int
        The number of the label in all labels for the label manager.

    .. note:: Labels and references comprise a few components:

              label: {name} {document_number}.{number}{separator} {caption}

                  ex: Fig. 2.1. My first figure on the second chapter.

                      name: 'Fig.'
                      document_number: '2
                      number: 1 (the local_order number in the document)
                      seperator: '.'
                      caption: 'My first figure on the second chapter'

              Labels and references take a format (string) that can be used
              to format the label or reference. A kwargs dict is passed with
              the following variables.

              - name: the name of the label. ex: 'Fig.', 'Section', 'Chapter'
              - document_number: the number (order) of the document, starting
                from 1.
              - local_number: the number (order) of the label within the
                document.
              - global_number: the number (order) of the label between all
                documents in the label manager.
              - separator: a character or string to end the label. ex: '.'
              - caption: The caption of the label linked to this label.
              - short: The short caption of the label linked to this label.

    """
    __slots__ = ('document', 'kind', 'id', 'contents', 'label_type',
                 'local_order', 'global_order')

    # TODO: add format
    def __init__(self, document, kind, id, contents=None, label_type='short',
                 local_order=None, global_order=None):
        self.document = document
        self.kind = kind
        self.id = id
        self.contents = contents
        self.label_type = label_type
        self.local_order = local_order
        self.global_order = global_order

    def __repr__(self):
        name = self.id if self.id is not None else self.contents
        return "({} {})".format(name, self.global_order)

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
        # Get the format string for the short label. Start from the most
        # specific kind to the least specific.
        text = None

        for kind in reversed(self.kind):
            # Look in the local_context, global_context and the settings,
            # in that order
            if text is not None:
                # The format text is found! We don't need to look anymore
                break
            for d in (local_context, global_context, settings.label_format):
                if kind in d:
                    # See if a format for the kind tuple is available
                    text = local_context[kind]
                    break
        if text is None:
            text = self.contents
            # text = self.kind[-1]

        # Get the document's number
        if (isinstance(local_context, dict) and
           'document_number' in local_context):
            document_number = (local_context['document_number'] if
                               'document_number' in local_context else '')
        else:
            document_number = ''

        # Get the number of the label from the most specific kind
        number = str(self.local_order[-1])

        # Format the text
        text = text.format(number=number, document_number=document_number)

        return text

    #TODO: def label(format="...")
    def label(self, local_context=None, global_context=None,
              end=settings.label_sep):
        """The text label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.
        end : str
            Add the following string to the end.

        Returns
        -------
        label : str
            The text label
        """
        if self.label_type == 'short':
            return self.short(local_context, global_context) + end
        else:
            return self.contents

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
        specific_kind = self.kind[-1]
        attrs = {'class': specific_kind + '-label',
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
        if self.kind[-1] != 'document':
            anchor = '#' + self.id if isinstance(self.id, str) else ''
        else:
            anchor = ''

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
            link = "/" + location_file + anchor

        text = self.label(local_context, global_context, end='')

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
        return self.label(local_context, global_context, end='')


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
    _local_counters = None
    _global_counter = None

    def __init__(self):
        self.labels = set()
        self._local_counters = dict()
        self._global_counter = dict()

    def add_label(self, document, kind, id=None, contents=None,
                  label_type='short',):
        """Add a label.

        Parameters
        ----------
        document : :obj:`disseminate.Document`
            The document (:obj:`disseminate.Document`) that owns this label.
        kind : tuple or str
            The kind of the label. ex: 'figure', 'chapter', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.
        contents : str, optional
            The short description for the label that can be used as the
            reference.
        label_type : str, optional
            The label to show when constructing references for the label.
            options: 'short', 'caption'

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
                raise DuplicateLabel(msg.format(label.name,
                                                label.document.src_filepath))

        # Get the counter for this document
        counter = self._local_counters.setdefault(src_filepath, dict())
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

        # # Get the local_number and global_number of this label, based on
        # # current counts
        # kind_labels = {i for i in self.labels if i.kind == kind}
        # global_number = len(kind_labels) + 1
        # local_number = len([i for i in kind_labels
        #                     if i.src_filepath == src_filepath]) + 1

        # Add the label
        label = Label(document=document, kind=kind, id=id, contents=contents,
                      label_type=label_type, local_order=tuple(local_order),
                      global_order=tuple(global_order))
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
            document_labels = sorted([l for l in self.labels
                                      if l.document == document],
                                     key=lambda x: x.global_order)
        else:
            document_labels = sorted([l for l in self.labels],
                                     key=lambda x: x.global_order)

        if kinds is None:
            return list(document_labels)

        # Filter labels by kind
        if isinstance(kinds, str):
            kinds = [kinds]

        returned_labels = []
        for kind in kinds:
            returned_labels += [l for l in document_labels if kind in l.kind]

        return returned_labels

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
        self._local_counters.clear()
        self._global_counter.clear()
        for label in sorted(self.labels, key=lambda i: i.global_order):
            src_filepath = label.document.src_filepath
            counter = self._local_counters.setdefault(src_filepath, dict())
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
