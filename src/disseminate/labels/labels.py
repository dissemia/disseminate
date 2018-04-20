import os.path

from lxml.builder import E

from .. import settings
from ..attributes import get_attribute_value


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
        name = self.id if self.id else ''
        return "({}: {} {})".format(self.kind, name, self.global_order)

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


