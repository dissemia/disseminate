import os.path

from lxml.builder import E

from .. import settings
from ..attributes import get_attribute_value


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

    Parameters
    ----------
    document : :obj:`disseminate.Document`
        The document that owns the label.
    tag : None or :obj:`disseminate.Tag`
        The tag that owns the label.
    kind : tuple or None
        The kind of the label is a tuple that identified the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'h1',)
    id : str or None
        The (unique) identifier of the label. ex: 'nmr_introduction'.
        If None is given, the label cannot be referenced; it is used for
        counting only.
    contents : str, optional
        The short description for the label that can be used in the reference.
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
    __slots__ = ('document', 'tag', 'kind', 'id', 'local_order', 'global_order')

    def __init__(self, document, tag=None, kind=None, id=None,
                 local_order=None, global_order=None):
        self.document = document
        self.tag = tag
        self.kind = kind if kind is not None else ('default',)
        self.id = id
        self.local_order = local_order
        self.global_order = global_order

    def __repr__(self):
        name = self.id
        return "({} {})".format(name, self.global_order)

    @property
    def src_filepath(self):
        """The src_filepath of the document which owns this label."""
        assert (self.document is None and not
                hasattr(self.document, 'src_filepath'),
                "A document must own the label '{}'".format(self))
        return self.document.src_filepath

    def format_str(self, name, target):
        """Get the format string for the given format string name.

        Parameters
        ----------
        name : str
            The name of the format_str to get. Either 'label', 'ref' or 'link

        Returns
        -------
        format_str : str
            The format string for the given name.

        .. note:: The format string can be specified in a few ways, in the
                  following (decreasing) order of preference.

                  1. The label's tag attributes. A format string can be
                     specified. ex: @ref[label='Fig. {number}' html.link='/']
                  2. The local_context. The format string is found from the
                     kind of label. ex: 'figure_label': {Fig. 'number'}
                  3. The global_context. The format string is found from the
                     kind of label. ex: 'figure_label': {Fig. 'number'}
                  4. The settings. The format string is found from the kind
                     of label in the 'label_formats' dict.
        """
        # See if the format_str is in the local_context or global context
        # Try look for the kind of label, starting from the most specific
        # (last item) to the least. Use default values last.
        for kind in list(reversed(self.kind)) + ['default']:
            context_label = kind + '_' + name  # ex: 'figure_label'
            context_target_label = context_label + '_' + target.strip('.')

            contexts = (getattr(self.document, 'local_context', None),
                        getattr(self.document, 'global_context', None))
            for context in contexts:
                if context is None:
                    continue
                if context_target_label in context:
                    return context[context_target_label]
                if context_label in context:
                    return context[context_label]

            # Finally, try to get a default format_str from the settings, if one
            # couldn't be found in the tag
            if context_target_label in settings.label_formats:
                return settings.label_formats[context_target_label]
            if context_label in settings.label_formats:
                return settings.label_formats[context_label]

        return ''

    def format_kwargs(self):
        """Forumlate a kwargs dict used for making labels and references for
        this label.

        Returns
        -------
        kwargs : dict
            A dict of values used for the labels and references, including:
            - name: A default name of the label. ex: 'Figure', 'Section',
                    'Chapter'
            - document_number: the number (order) of the document,
              starting from 1.
            - number: the number (order) of the label within the document.
              (this is the same as the local_number)
            - global_number: the number (order) of the label between all
              documents in the label manager.
            - content: The content of the tag that owns this label.
            - short: The short content of the tag linked to this label.
        """
        kwargs = dict()
        kwargs['name'] = self.kind[-1].title()
        kwargs['number'] = self.local_order[-1]
        kwargs['local_number'] = self.local_order[-1]
        kwargs['global_number'] = self.global_order[-1]
        kwargs['id'] = self.id if self.id is not None else ''

        # Get values from the document
        kwargs['document_number'] = (self.document.number
                                     if self.document.number is not None
                                     else '')
        kwargs['content'] = self.document.title
        kwargs['short'] = self.document.short

        # Overwrite with values from the tag, if available
        if self.tag is not None:
            kwargs['content'] = (self.tag.content
                                 if hasattr(self.tag, 'content')
                                 else '')

            short = get_attribute_value(attrs=self.tag.attributes,
                                        attribute_name='short')
            kwargs['short'] = short if short is not None else kwargs['content']

        return kwargs

    def label(self, target, label_str=None):
        """Generate the label.

        Parameters
        ----------
        target : str
            The target format to generate the label for. (ex: '.html', '.tex')
        label_str : str or None, optional
            If a format_str is given, it will be used rather than the one
            returned from this class's format_str method.

        Returns
        -------
        label : str or html element
            The label.

        .. note:: The label method makes the following variables available to
                  formatted strings.

        """
        label_str = (self.format_str(name='label', target=target)
                     if label_str is None else label_str)
        kwargs = self.format_kwargs()
        if target == '.html':
            # Make a span element for html labels
            tag_kwargs = dict()
            if self.id:
                tag_kwargs['id'] = self.id
            tag_kwargs['class'] = self.kind[-1] + '-' + 'label'
            return E('span', label_str.format(**kwargs), **tag_kwargs)
        else:
            # Otherwise just return the text
            return label_str.format(**kwargs)

    def ref(self, target, ref_str=None, link_str=None):
        """

        Parameters
        ----------
        target
        label_format

        Returns
        -------

        """
        ref_str = (self.format_str(name='ref', target=target)
                   if ref_str is None else ref_str)
        link_str = (self.format_str(name='link', target=target)
                    if link_str is None else link_str)
        kwargs = self.format_kwargs()
        kwargs['filepath'] = self.document.target_filepath(target=target,
                                                           render_path=False)

        if target == '.html':
            tag_kwargs = dict()
            tag_kwargs['class'] = self.kind[-1] + '-' + 'ref'
            tag_kwargs['href'] = link_str.format(**kwargs)

            return E('a', ref_str.format(**kwargs), **tag_kwargs)
        else:
            # Otherwise just return the text
            return ref_str.format(**kwargs)


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

        # Add the label
        label = Label(document=document, tag=tag, kind=kind, id=id,
                      local_order=tuple(local_order),
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
