import os.path

from lxml.builder import E

from .. import settings


class DuplicateLabel(Exception):
    """A label that was already defined is defined again"""
    pass


class LabelNotFound(Exception):
    """Could not find a reference to a label"""
    pass


class Label(object):
    """A label used for referencing

    Parameters
    ----------
    kind : str
        The kind of the label. ex: 'figure', 'chapter', 'equation'
    id : str or None
        The (unique) identifier of the label. ex: 'nmr_introduction'.
        If None, then it's a generic label used to keep count.
    contents : str, optional
        The short description for the label that can be used as the reference.
    src_filepath : str
        The src_filepath of the document that owns this label.
    targets : dict of str
        The targets for the document that owns this label. The target_filepaths
        are relative to the target root, including the segregate target.
        (i.e. not a render path)
    local_number : int
        The number of the label in the current document.
    global_number : int
        The number of the label in the project.
    """
    __slots__ = ('kind', 'id', 'contents', 'src_filepath', 'targets',
                 'local_number', 'global_number')

    def __init__(self, kind, id, contents, src_filepath, targets, local_number,
                 global_number):
        self.kind = kind
        self.id = id
        self.contents = contents
        self.src_filepath = src_filepath
        self.targets = targets
        self.local_number = local_number
        self.global_number = global_number

    def __repr__(self):
        return "({} {}-{})".format(self.id, self.local_number,
                                   self.global_number)

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

    def html_label(self, local_context=None, global_context=None):
        """The html label (anchor) for this label.

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
        text = self.short(local_context, global_context)
        attrs = {'class': self.kind + '-label',
                 'id': self.id}
        return E('span', text, **attrs)

    def html_ref(self, short=True, local_context=None, global_context=None):
        """An html reference link to this label.

        Parameters
        ----------
        short : bool, optional
            Use the short description for the link. Otherwise use the long.
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

        # See if it's on a different document from the src_filepath
        if (isinstance(local_context, dict) and
           local_context['_src_filepath'] == self.src_filepath):
            # the documents match, make an internal link
            link = "#" + self.id
        else:
            # the documents match, make an internal link
            link = self.targets['.html'] + "#" + self.id

        text = self.short(local_context, global_context)

        return E('a', text, href=link)

    def tex_ref(self, short=True, local_context=None, global_context=None):
        """An tex reference to this label.

        Parameters
        ----------
        short : bool, optional
            Use the short description for the link. Otherwise use the long.
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

    Parameters
    ----------
    project_root : str
        The root directory for the document (source markup) files. (i.e. the
        input directory)
        ex: 'src/'
    target_root : str
        The target directory for the output documents (i.e. the output
        directory). The final output directory also depends on the
        segregate_targets option.
        ex: 'out/'
    segregate_targets : bool, optional
        If True (short), the processed output documents for each target type
        will be place in its directory named for the target.
        ex: 'out/html'

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

    project_root = None
    target_root = None
    segregate_targets = None
    labels = None

    def __init__(self, project_root, target_root,
                 segregate_targets=settings.segregate_targets):
        self.project_root = project_root
        self.target_root = target_root
        self.segregate_targets = segregate_targets
        self.labels = set()

    def target_path(self, target):
        """The final render path for the given target."""
        if self.segregate_targets:
            return os.path.join(self.target_root, target.strip('.'))
        else:
            return self.target_root

    def add_label(self, local_context, global_context, kind, id=None,
                  contents=None):
        """Add a label.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.
        kind : str
            The kind of label. ex: 'chapter', 'figure', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.
        contents : str, optional


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
        # Get the current counters
        assert '_src_filepath' in local_context
        assert '_targets' in local_context
        src_filepath = local_context['_src_filepath']
        targets = local_context['_targets']

        # Check to see if a label is unique for a project. A generic label id
        # (i.e. None) is guaranteed to be unique
        if id is not None:
            existing_labels = {i for i in self.labels if i.id == id}

            if existing_labels:
                label = existing_labels.pop()
                msg = "The label '{}' was already defined by the document {}."
                raise DuplicateLabel(msg.format(label.name,
                                                label.document.src_filepath))

        # The label's targets are relative to the target's directory.
        # Create these targets from the document's targets
        label_targets = {k: os.path.relpath(v, self.target_path(k))
                         for k, v in targets.items()}

        # Get the local_number and global_number of this label, based on
        # current counts
        kind_labels = {i for i in self.labels if i.kind == kind}
        global_number = len(kind_labels) + 1
        local_number = len([i for i in kind_labels
                            if i.src_filepath == src_filepath]) + 1

        # Add the label
        label = Label(kind=kind, id=id, contents=contents, targets=label_targets,
                      local_number=local_number, global_number=global_number,
                      src_filepath=src_filepath)
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

    def reset(self, document_src_filepath=None):
        """Reset the labels tracked by the LabelManager.

        Parameters
        ----------
        document_src_filepath : str or None
            If specified, remove all dependencies for the given src_filepath of
            a document markup source file for all targets.
            If not specified (None), all dependencies are removed.
        """
        if isinstance(document_src_filepath, str):
            # Go through all labels
            labels_to_remove = set()
            for label in self.labels:
                # Find the labels that match the document_src_filepath
                if label.src_filepath == document_src_filepath:
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

                sf = label.src_filepath
                local_numbers[sf] = local_numbers.setdefault(sf, 0) + 1

                label.local_number = local_numbers[sf]
