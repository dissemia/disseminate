import time
import weakref

from ..tags import settings as tag_settings
from ..tags import Tag


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
    contents : str, optional
        The short description for the label that can be used in the reference.
    local_order : tuple of int or None
        The number of the label in the current document. Since the kind is a
        tuple, the local_order corresponds to the count for each kind.
        ex: for a kind ('heading', 'h2') could have a local_order of (3, 2)
        which would represent the 3rd 'heading' and 2nd 'h2' item for a
        document.
    global_order : tuple of int or None
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
    __slots__ = ('id', '_document', '_tag', '_kind',
                 '_local_order', '_global_order',
                 '_document_label', '_chapter_label', '_section_label',
                 '_subsection_label', '_subsubsection_label',
                 'mtime', '__weakref__')

    def __init__(self, document, id=None, tag=None, kind=None,
                 local_order=None, global_order=None,):
        self.document = document
        self.id = id
        self.tag = tag
        self._kind = kind if kind is not None else ('default',)
        self._local_order = local_order
        self._global_order = global_order
        self._document_label = None
        self._chapter_label = None
        self._section_label = None
        self._subsection_label = None
        self._subsubsection_label = None
        self.mtime = time.time()

    def __repr__(self):
        name = self.id if self.id else ''
        return "({}: {} {})".format(self.kind, name, self.global_order)

    @property
    def document(self):
        return (self._document() if hasattr(self, '_document') and
                callable(self._document) else None)

    @document.setter
    def document(self, value):
        old_value = self.document
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._document = weakref.ref(value)

    @property
    def document_number(self):
        document = self.document
        if document is not None:
            return document.number or 0
        else:
            return 0

    @property
    def tag(self):
        return (self._tag() if hasattr(self, '_tag') and
                callable(self._tag) else None)

    @tag.setter
    def tag(self, value):
        old_value = self.tag
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._tag = weakref.ref(value)

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        if value != self._kind:
            self.mtime = time.time()
            self._kind = value

    @property
    def local_order(self):
        return self._local_order

    @local_order.setter
    def local_order(self, value):
        if value != self._local_order:
            self.mtime = time.time()
            self._local_order = value

    @property
    def global_order(self):
        return self._global_order

    @global_order.setter
    def global_order(self, value):
        if value != self._global_order:
            self.mtime = time.time()
            self._global_order = value

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

        title = Tag.default(tag)  # The parent default functions is called to
                                  # avoid recursions when labels refer to a
                                  # tag's title.
        title_lines = list(filter(bool, title.split('\n')))  # remove extra
                                                             # newlines

        if len(title_lines) > 0:
            # Find the first line with a period.
            new_lines = []
            for line in title_lines:
                # Get the string up to a period and strip extra space
                partition = line.partition('.')
                new_lines.append(partition[0].strip())

                # If a period was found, then the title is done.
                if partition[1] == '.':
                    break
            return " ".join(new_lines)
        else:
            return ""

    @property
    def short(self):
        """The short title for the tag or document."""
        tag = self.tag
        if tag is None or not hasattr(tag, 'short'):
            # Get the short from the document
            return self.document.short if self.document is not None else ""

        return tag.short if tag is not None else ""

    @property
    def content(self):
        """The content of the tag."""
        tag = self.tag
        return tag.content if tag is not None else None

    @property
    def document_label(self):
        return (self._document_label() if hasattr(self, '_document_label') and
                callable(self._document_label) else None)

    @document_label.setter
    def document_label(self, value):
        old_value = self.document_label
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._document_label = weakref.ref(value)

    @property
    def chapter_label(self):
        if self._chapter_label is not None and callable(self._chapter_label):
            return self._chapter_label()
        elif self.kind[-1] == 'chapter':
            return self
        else:
            return None

    @chapter_label.setter
    def chapter_label(self, value):
        old_value = self.chapter_label
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._chapter_label = weakref.ref(value)

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
    def section_label(self):
        if self._section_label is not None and callable(self._section_label):
            return self._section_label()
        elif self.kind[-1] == 'section':
            return self
        else:
            return None

    @section_label.setter
    def section_label(self, value):
        old_value = self.section_label
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._section_label = weakref.ref(value)

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
    def subsection_label(self):
        if (self._subsection_label is not None and
           callable(self._subsection_label)):
            return self._section_label()
        elif self.kind[-1] == 'subsection':
            return self
        else:
            return None

    @subsection_label.setter
    def subsection_label(self, value):
        old_value = self.subsection_label
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._subsection_label = weakref.ref(value)

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
    def subsubsection_label(self):
        if (self._subsubsection_label is not None and
           callable(self._subsubsection_label)):
            return self._section_label()
        elif self.kind[-1] == 'subsubsection':
            return self
        else:
            return None

    @subsubsection_label.setter
    def subsubsection_label(self, value):
        old_value = self.subsubsection_label
        if value != old_value and value is not None:
            self.mtime = time.time()
            self._subsubsection_label = weakref.ref(value)

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
        label_sep = tag_settings.label_fmt['label_sep']

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
        return self.document.src_filepath
