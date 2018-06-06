import time
import weakref

from .. import settings


class Label(object):
    """A label used for referencing.

    Parameters
    ----------
    document : :obj:`disseminate.Document`
        The document that owns the label.
    id : str or None
        The (unique) identifier of the label. ex: 'nmr_introduction'.
        If None is given, the label cannot be referenced; it is used for
        counting only.
    tag : None or :obj:`disseminate.Tag`
        The tag that owns the label.
    kind : tuple or None
        The kind of the label is a tuple that identified the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'h1',)
    local_order : tuple of int or None
        The number of the label in the current document. Since the kind is a
        tuple, the local_order corresponds to the count for each kind.
        ex: for a kind ('heading', 'h2') could have a local_order of (3, 2)
        which would represent the 3rd 'heading' and 2nd 'h2' item for a
        document.
    global_order : tuple of int or None
        The number of the label in all labels for the label manager.
    """

    # The following attributes are stored as weak references
    weakref_attrs = ('_document', '_tag', '_document_label',
                     '_chapter_label', '_section_label',
                     '_subsection_label', '_subsubsection_label')

    # The following attributes will not update the mtime if replaced. This
    # includes the 'tag', since this is recreated every time the AST is reloaded
    # and it contains its own 'mtime'
    exclude_update = ('document', 'tag', 'kind')

    def __init__(self, document, id=None, tag=None, kind=None,
                 local_order=None, global_order=None,):
        self.document = document
        self.id = id
        self.tag = tag
        self.kind = kind if kind is not None else ('default',)
        self.local_order = local_order
        self.global_order = global_order

    def __repr__(self):
        name = self.id if self.id else ''
        return "({}: {} {})".format(self.kind, name, self.global_order)

    @property
    def mtime(self):
        document = self.document
        mtimes = []
        if document is not None and 'mtime' in document.context:
            mtimes.append(document.context['mtime'])

        tag = self.tag
        if tag is not None and 'mtime' in tag.context:
            mtimes.append(tag.context['mtime'])

        # Get the latest mtime
        mtime = self.__dict__.get('mtime')
        if mtime is not None:
            mtimes.append(mtime)

        return max(mtimes) if len(mtimes) > 0 else None

    def __getattr__(self, name):
        attr_name = '_' + name
        attr = (self.__dict__.get(attr_name, None) or
                self.__dict__.get(name, None))
        return attr() if callable(attr) else attr

    def __setattr__(self, name, value):

        # Determine the attribute's name
        attr_name = '_' + name

        # Get the current value. Dereference the weakref link, if needed.
        current_value = (getattr(self, attr_name, None) or
                         getattr(self, name, None))
        current_value = (current_value() if callable(current_value) else
                         current_value)

        if value is None:
            return

        # Set the value, and create a weakref if needed
        if attr_name in self.weakref_attrs:
            self.__dict__[attr_name] = weakref.ref(value)
        else:
            self.__dict__[attr_name] = value

        # Set the mtime if the value is changed or it has already been set
        if (name not in self.exclude_update and
            current_value != value and
            current_value is not None):
            self.__dict__['mtime'] = time.time()

    @property
    def document_number(self):
        document = self.document
        if document is not None:
            return document.number or 0
        else:
            return 0

    @property
    def number(self):
        """The (local) number for the label's kind."""
        return self._local_order[-1]

    @property
    def global_number(self):
        """The (global) number for the label's kind."""
        return self._global_order[-1]

    @property
    def title(self):
        """The title for the label from the tag's content.

        The title is defined as the first sentence or line.
        """
        tag = self.tag
        if tag is None:
            return self.document.title if self.document is not None else ""
        else:
            return tag.title

    @property
    def short(self):
        """The short title for the tag or document."""
        tag = self.tag
        if tag is None:
            # Get the short from the document
            return self.document.short if self.document is not None else ""
        else:
            return tag.short

    @property
    def content(self):
        """The content of the tag."""
        tag = self.tag
        return tag.content if tag is not None else None

    @property
    def chapter_number(self):
        chapter_label = self.chapter_label
        return (chapter_label.global_order[-1] if chapter_label is not None
                else '')

    @property
    def chapter_title(self):
        chapter_label = self.chapter_label
        return chapter_label.title if chapter_label is not None else ''

    @property
    def section_number(self):
        section_label = self.section_label
        return (section_label.local_order[-1] if section_label is not None
                else '')

    @property
    def section_title(self):
        section_label = self.section_label
        return section_label.title if section_label is not None else ''

    @property
    def subsection_number(self):
        subsection_label = self.subsection_label
        return (subsection_label.local_order[-1] if subsection_label is not None
                else '')

    @property
    def subsection_title(self):
        subsection_label = self.subsection_label
        return subsection_label.title if subsection_label is not None else ''

    @property
    def subsubsection_number(self):
        subsubsection_label = self.subsubsection_label
        return (subsubsection_label.local_order[-1] if subsubsection_label is
                not None else '')

    @property
    def subsubsection_title(self):
        subsubsection_label = self.subsubsection_label
        return (subsubsection_label.title if subsubsection_label is not None
                else '')

    @property
    def tree_number(self):
        """The string for the number for the chapter, section, subsection and
        so on. i.e. Section 3.2.1."""
        # Get a tuple of the numbers, remove empty string items and None
        numbers = filter(bool, (self.chapter_number,
                                self.section_number,
                                self.subsection_number,
                                self.subsubsection_number))

        # Convert the numbers to strings
        numbers = map(str, numbers)

        # Get the label separator character, first from the settings module,
        # then, if available, in the context or the tag's attributes
        label_sep = settings.label_fmt['label_sep']

        if self.tag is not None:
            # Replace with a value in the context, if available
            if 'label_sep' in self.tag.context:
                label_sep = self.tag.context['label_sep']

            # Replace with a value in the tag's attributes, if available
            label_sep_attr = self.tag.get_attribute('label_sep', clear=True)
            label_sep = label_sep if label_sep_attr is None else label_sep_attr

        # Return a string with the numbers joined by a character.
        return label_sep.join(numbers)

    @property
    def src_filepath(self):
        """The src_filepath of the document which owns this label."""
        document = self.document
        return self.document.src_filepath if document is not None else None
