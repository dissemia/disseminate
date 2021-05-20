"""
The Ref tag to reference captions and other labels.
"""
from .tag import Tag
from .exceptions import assert_content_str
from .utils import content_to_str, format_content
from ..label_manager.types import DocumentLabel
from ..signals import signal
from ..formats import xhtml_tag, tex_cmd


ref_label_dependencies = signal("ref_label_dependencies")


@ref_label_dependencies.connect_via(order=1000)
def add_ref_labels(builder, **kwargs):
    """Find and add the labels associated with Ref tags for all tags in
    the context.
    """
    context = builder.context

    # Find tags in the context and get the ref tag labels
    ref_label_ids = set()
    for tag in filter(lambda t: isinstance(t, Tag), context.values()):
        # Flatten the tag tree
        flat_tags = tag.flatten(filter_tags=True)

        # Retrieve all Ref tags and their label ids
        ids = [t.label_id for t in flat_tags if isinstance(t, Ref)]
        ref_label_ids.update(ids)

    # Remove None entries
    ref_label_ids.discard(None)

    # Retrieve the labels
    label_man = context.get('label_manager')
    if label_man is not None and ref_label_ids:
        return sorted(label_man.get_labels_by_id(ids=ref_label_ids))
    else:
        return []


class RefError(Exception):
    """A reference to a document could not be found."""
    pass


class Ref(Tag):
    """A tag to reference a label.

    Attributes
    ----------
    doc_id : str
        The doc_id for the document that owns the label referenced. This
        might be different to the doc_id listed in the context if a reference
        is made to a label in another document.
    label_id : str
        The id of the label referenced by this tag.

    .. note:: The ref tag takes the label id as the content. If the label is
              not found, a label manager exception is raised.
              (:exc:`.label_manager.exceptions.LabelNotFound`)
    """

    active = True

    doc_id = None
    label_id = None

    def __init__(self, name, content, *args, **kwargs):
        assert_content_str(content)

        super(Ref, self).__init__(name, content, *args, **kwargs)

        # Set the label_id and doc_id
        self.label_id = self.content.strip()

    @property
    def label(self):
        """Retrieve the label for this ref tag."""
        assert self.context.is_valid('label_manager')
        label_manager = self.context['label_manager']
        if self.label_id is not None:
            return label_manager.get_label(id=self.label_id)
        else:
            return None

    def document(self, cache=None):
        """The document that owns the label referenced by this tag.

        Parameters
        ----------
        cache : Optional[dict]
            If specified, the cache values will be used instead of being
            evaluated. Possibilities:
            - 'label': :obj:`.types.Label`
            - 'documents_by_id': Dict[str, :obj:`document.Document`]

        Returns
        -------
        document : Union[:obj:`Document <.Document>`, None]
            The document that owns the label referenced by this tag, if
            available.
            None, if a document could not be found.
        """
        assert self.context.is_valid('root_document')
        cache = dict() if cache is None else cache
        label = cache.setdefault('label', self.label)
        documents_by_id = cache.get('documents_by_id', None)

        # Get the doc_ids for the document that owns this tag (doc_id) and
        # the document that owns the label (other_doc_id)
        doc_id = self.context.get('doc_id', None)
        other_doc_id = label.doc_id

        if doc_id is not None and doc_id == other_doc_id:
            # Return this document, if the label is owned by the same document
            # as the owner of this tag.
            return self.context.document

        # The other_doc_id and doc_id are different, so this Ref tag references
        # a label owned by another document.
        #
        # Fetch the root document to figure out which document corresponds to
        # the doc_id of this ref tag's label.
        if documents_by_id is None:
            root_document = (self.context['root_document']()
                             if 'root_document' in self.context else
                             None)  # de-reference root document, if available
            docs_by_doc_ids = (root_document.documents_by_id(recursive=True)
                               if root_document is not None else None)
        else:
            docs_by_doc_ids = documents_by_id

        if other_doc_id in docs_by_doc_ids:
            return docs_by_doc_ids[other_doc_id]
        else:
            return None

    def url(self, target='.html', include_anchor=True, cache=None):
        """The url path for the document referenced by the label for this tag.

        Parameters
        ----------
        target : Optional[str]
            The target extension for the target file.
            ex: '.html' or '.tex'
        include_anchor : Optional[bool]
            If True (default), the html link anchor will be appended to the
            url path.
        cache : Optional[dict]
            If specified, the cache values will be used instead of being
            evaluated. Possibilities:
            - 'label': :obj:`.types.Label`
            - 'documents_by_id': Dict[str, :obj:`document.Document`]

        Returns
        -------
        url_path : str
            The url path for the document owning the label referenced by this
            tag.
        """
        context = self.context
        cache = dict() if cache is None else cache
        assert context.is_valid('doc_id')

        # Format the target string
        target = (target if target.startswith('.') else '.' + target)

        # Get the doc_ids for the document that owns this tag (doc_id) and
        # the document that owns the label (other_doc_id). See if they're the
        # same document, in which case an internal link is returned.
        label = cache.setdefault('label', self.label)
        doc_id = self.context.get('doc_id', None)
        other_doc_id = label.doc_id if label is not None else None

        if doc_id is None or other_doc_id is None:
            msg = ("Could not find the tag or label document for the ref tag "
                   "'{}'")
            raise RefError(msg.format(self))
        elif doc_id is not None and doc_id == other_doc_id:
            return '#' + label.id if include_anchor else ''

        # In this case, the label and tag documents are different. Return a
        # link to the label's document.
        document = self.document(cache=cache)
        target_filepath = document.target_filepath(target)

        if target_filepath is None:
            return None

        link = target_filepath.get_url(context=self.context)

        return link + '#' + label.id if include_anchor else link

    def default_fmt(self, content=None, attributes=None, cache=None, **kwargs):
        """Convert the tag to a text string.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.
        cache : Optional[dict]
            If specified, the cache values will be used instead of being
            evaluated. Possibilities:
            - 'label': :obj:`.types.Label`
            - 'documents_by_id': Dict[str, :obj:`document.Document`]

        Returns
        -------
        text_string : str
            A text string with the tags stripped.
        """
        # Get the label tag format
        label_manager = self.context.get('label_manager')
        context = self.context
        cache = dict() if cache is None else cache
        label = cache.setdefault('label', self.label)

        if all(i is not None for i in (label_manager, label, context)):
            # Format the format string keys for a ref
            keys = ('ref', *label.kinds)
            format_str = label_manager.format_string(id=self.label.id, *keys)

            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            return content_to_str(processed_tag.content)
        else:
            return ''

    def tex_fmt(self, content=None, attributes=None, mathmode=False,
                cache=None, level=1, **kwargs):
        """Format the tag in LaTeX format.

        .. note:: This function renders tex links to compiled pdf documents

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.
        mathmode : Optional[bool]
            If True, the tag will be rendered in math mode. Otherwise (default)
            latex text mode is assumed.
        cache : Optional[dict]
            If specified, the cache values will be used instead of being
            evaluated. Possibilities:
            - 'label': :obj:`.types.Label`
            - 'documents_by_id': Dict[str, :obj:`document.Document`]
        level : Optional[int]
            The level of the tag.

        Returns
        -------
        tex_string : str
            The formatted tex string.
        """
        label_manager = self.context.get('label_manager')
        context = self.context
        cache = dict() if cache is None else cache
        label = cache.setdefault('label', self.label)

        if all(i is not None for i in (label_manager, label, context)):
            # Retrieve the format string for the reference
            keys = ('ref', *label.kind)
            format_str = label_manager.format_string(label.id, *keys,
                                                     target='.tex')

            # process the tags and format the contents
            # for html
            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            content = format_content(content=processed_tag.content,
                                     format_func='tex_fmt', level=level + 1)

            # setup a url path and include the anchor if the label is not
            # for a DocumentLabel. DocumentLabels should just point to the
            # file itself.
            # Tex formats will only work with pdf links
            include_anchor = not isinstance(label, DocumentLabel)

            url = self.url(target='.pdf', include_anchor=include_anchor,
                           cache=cache)

            # Add a target-specific attribute to the url so that it's
            # properly parsed for the '.tex' target
            url = url + '.tex' if url else ''

            # wrap content in 'href' tag, if a url is present, otherwise
            # just return a regular text string
            return (tex_cmd('href', attributes=url, formatted_content=content)
                    if url else content)
        else:
            return ''

    def html_fmt(self, content=None, attributes=None, cache=None,
                 format_func='html_fmt', method='html', level=1, **kwargs):
        """Convert the tag to an (x)html string or (x)html element.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.
        cache : Optional[dict]
            If specified, the cache values will be used instead of being
            evaluated. Possibilities:
            - 'label': :obj:`.types.Label`
            - 'documents_by_id': Dict[str, :obj:`document.Document`]
            - 'format_str': str
        format_func : Optional[str]
            The tag format function to use in rendering the reference tag.
            (ex: 'html_fmt' or 'xhtml_fmt')
        method : Optional[str]
            The rendering method for the string. ex: 'html' or 'xml'
        level : Optional[int]
            The level of the tag.

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        label_manager = self.context.get('label_manager')
        cache = dict() if cache is None else cache
        label = cache.setdefault('label', self.label)
        context = self.context

        if all(i is not None for i in (label_manager, label, context)):

            # Retrieve the format string for the reference
            # Use the 'html' format_str for html and xhtml
            keys = ('ref', *label.kind)
            format_str = label_manager.format_string(label.id, *keys,
                                                     target='.html')

            # substitute the link, process the tags and format the contents
            # for html (html_fmt) or xhtml (xhtml_fmt)
            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            content = format_content(content=processed_tag.content,
                                     format_func=format_func, level=level + 1)

            attrs = (self.attributes.copy() if attributes is None else
                     attributes)
            attrs['class'] = 'ref'

            # setup the url path and include the anchor if the label is not
            # for a DocumentLabel. DocumentLabels should just point to the
            # file itself.
            include_anchor = not isinstance(label, DocumentLabel)
            attrs['href'] = self.url(target=method, cache=cache,
                                     include_anchor=include_anchor)

            # wrap content in 'a' tag
            return xhtml_tag('a', attributes=attrs, formatted_content=content,
                             level=level, method=method,
                             pretty_print=False)  # no line breaks
        else:
            return ''
