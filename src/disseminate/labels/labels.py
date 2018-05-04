import time
import weakref

from lxml.builder import E

from .. import settings
from ..attributes import get_attribute_value


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
                  2. The context. The format string is found from the
                     kind of label. ex: 'figure_label': {Fig. 'number'}
                  3. The settings. The format string is found from the kind
                     of label in the 'label_formats' dict.
        """
        # See if the format_str is in the local_context or global context
        # Try look for the kind of label, starting from the most specific
        # (last item) to the least. Use default values last.
        for kind in list(reversed(self.kind)) + ['default']:
            context_label = kind + '_' + name  # ex: 'figure_label'
            context_target_label = context_label + '_' + target.strip('.')
            context = self.document.context

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
        kwargs['id'] = self.id or ''

        # Get values from the document
        kwargs['document_number'] = self.document.number or ''
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

        # Get values from the chapter and section
        chapter_label = self.chapter_label
        kwargs['chapter_local_number'] = (chapter_label.local_order[-1] if
                                          chapter_label is not None else '')
        kwargs['chapter_global_number'] = (chapter_label.global_order[-1] if
                                           chapter_label is not None else '')
        kwargs['chapter_number'] = kwargs['chapter_global_number']

        section_label = self.section_label
        kwargs['section_local_number'] = (section_label.local_order[-1] if
                                          section_label is not None else '')
        kwargs['section_global_number'] = (section_label.global_order[-1] if
                                           section_label is not None else '')
        kwargs['section_number'] = kwargs['section_local_number']

        return kwargs

    def label(self, target, label_str=None):
        """Generate the label.

        Parameters
        ----------
        target : str
            The target format for the generated  label for.
            (ex: '.html', '.tex')
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
        """A reference to a label

        Parameters
        ----------
        target : str
            The target format for the generated reference.
            (ex: '.html', '.tex')
        ref_str : str or None, optional
            If a format_str is given, it will be used rather than the one
            returned from this class's format_str method for the reference.
        link_str : str or None, optional
            If a format_str is given, it will be used rather than the one
            returned from this class's format_str method for the link.

        Returns
        -------
        ref : str or html element
            The reference.
        """
        ref_str = (self.format_str(name='ref', target=target)
                   if ref_str is None else ref_str)
        link_str = (self.format_str(name='link', target=target)
                    if link_str is None else link_str)
        kwargs = self.format_kwargs()

        # See if the target is in the document's target_list and render a link
        # if it is.
        if target in self.document.target_list:
            filepath = self.document.target_filepath(target=target,
                                                     render_path=False)
            kwargs['filepath'] = filepath
            create_link = True
        else:
            create_link = False

        # Create a link if the label's document has an available target
        target_list = self.document.target_list
        if target == '.html' and create_link:
            tag_kwargs = dict()
            tag_kwargs['class'] = self.kind[-1] + '-' + 'ref'
            tag_kwargs['href'] = link_str.format(**kwargs)
            return E('a', ref_str.format(**kwargs), **tag_kwargs)
        elif target == '.tex' and create_link:
            return (link_str.format(**kwargs) if self.id is not None else
                    ref_str.format(**kwargs))
        else:
            # Otherwise just return the text
            return ref_str.format(**kwargs)

    def pageref(self, target, pageref_str=None):
        """A page reference to a label.

        This only pertains to media that generate pages, like pdfs and latex.

        Parameters
        ----------
        target : str
            The target format for the generated reference.
            (ex: '.html', '.tex')
        pageref_str : str or None, optional
            If a format_str is given, it will be used rather than the one
            returned from this class's format_str method for the reference.

        Returns
        -------
        pageref : str
            The pagereference.
        """
        if pageref_str is None and target != '.html':
            pageref_str = self.format_str(name='pageref', target=target)

        kwargs = self.format_kwargs()

        # Get the pageref
        if target == '.html':
            return ''
        else:
            return pageref_str.format(**kwargs)


