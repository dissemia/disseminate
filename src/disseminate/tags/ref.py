"""
The Ref tag to reference captions and other labels.
"""
from .tag import Tag
from .exceptions import assert_content_str
from .utils import content_to_str, format_content
from ..label_manager.types import DocumentLabel
from ..formats import html_tag, tex_cmd


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

    def __init__(self, name, content, attributes, context):
        assert_content_str(content)

        super(Ref, self).__init__(name, content, attributes, context)

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

    @property
    def document(self):
        """The document that owns the label referenced by this tag.

        Returns
        -------
        document : Union[:obj:`Document <.Document>`, None]
            The document that owns the label referenced by this tag, if
            available.
            None, if a document could not be found.
        """
        assert self.context.is_valid('root_document')

        label = self.label

        # Get the doc_ids for the document that owns this tag (doc_id) and
        # the document that owns the label (other_doc_id)
        doc_id = self.context.get('doc_id', None)
        other_doc_id = label.doc_id

        if doc_id is not None and doc_id == other_doc_id:
            # Return this document, if the label is owned by the same document
            # as the owner of this tag.
            return (self.context['document']() if 'document' in self.context
                    else None)  # document needs to be de-reference

        # The other_doc_id and doc_id are different, so this Ref tag references
        # a label owned by another document.
        #
        # Fetch the root document to figure out which document corresponds to
        # the doc_id of this ref tag's label.
        root_document = (self.context['root_document']()
                         if 'root_document' in self.context else
                         None)  # de-reference root document, if available
        docs_by_doc_ids = (root_document.documents_by_id(recursive=True)
                           if root_document is not None else None)

        if other_doc_id in docs_by_doc_ids:
            return docs_by_doc_ids[other_doc_id]
        else:
            return None

    def url(self, target='.html', include_html_anchor=True):
        """The url path for the document referenced by the label for this tag.

        Parameters
        ----------
        target : Optional[str]
            The target extension for the target file.
            ex: '.html' or '.tex'
        include_html_anchor : Optional[bool]
            If True (default), the html link anchor will be appended to the
            url path.

        Returns
        -------
        url_path : str
            The url path for the document owning the label referenced by this
            tag.
        """
        context = self.context
        assert context.is_valid('doc_id')

        # Format the target string
        target = (target if target.startswith('.') else '.' + target)

        # Get the doc_ids for the document that owns this tag (doc_id) and
        # the document that owns the label (other_doc_id). See if they're the
        # same document, in which case an internal link is returned.
        label = self.label
        doc_id = self.context.get('doc_id', None)
        other_doc_id = label.doc_id if label is not None else None

        if doc_id is None or other_doc_id is None:
            msg = ("Could not find the tag or label document for the ref tag "
                   "'{}'")
            raise RefError(msg.format(self))
        elif doc_id is not None and doc_id == other_doc_id:
            return ('#' + label.id
                    if 'html' in target and include_html_anchor
                    else '')

        # In this case, the label and tag documents are different. Return a
        # link to the label's document.
        document = self.document
        target_filepath = document.target_filepath(target)
        link = target_filepath.get_url(context=self.context)

        return (link + '#' + label.id
                if 'html' in target and include_html_anchor
                else link)

    @property
    def mtime(self):
        """The last modification time of the document that owns the label
        referenced by this tag."""
        # Get the mtime for the label
        label = self.label
        return label.mtime if label is not None else None

    def default_fmt(self, content=None):
        # Get the label tag format
        label_manager = self.context.get('label_manager')
        context = self.context
        label = self.label

        if all(i is not None for i in (label_manager, label, context)):
            # Format the format string keys for a ref
            keys = ('ref', *label.kinds)
            format_str = label_manager.format_string(id=self.label.id, *keys)

            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            return content_to_str(processed_tag.content)
        else:
            return ''

    def tex_fmt(self, content=None, mathmode=False, level=1):
        label_manager = self.context.get('label_manager')
        label = self.label
        context = self.context

        if all(i is not None for i in (label_manager, label, context)):
            # Retrieve the format string for the reference
            keys = ('ref', *label.kind)
            format_str = label_manager.format_string(label.id, *keys,
                                                     target='.tex')

            # substitute the link, process the tags and format the contents
            # for html
            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            content = format_content(content=processed_tag.content,
                                     format_func='tex_fmt', level=level + 1)

            # wrap content in 'hyperref' tag
            return tex_cmd('hyperref', attributes=label.id,
                           formatted_content=content)
        else:
            return ''

    def html_fmt(self, content=None, level=1):
        label_manager = self.context.get('label_manager')
        label = self.label
        context = self.context

        if all(i is not None for i in (label_manager, label, context)):

            # Retrieve the format string for the reference
            keys = ('ref', *label.kind)
            format_str = label_manager.format_string(label.id, *keys,
                                                     target='.html')

            # substitute the link, process the tags and format the contents
            # for html
            processed_tag = Tag(name='ref', content=format_str, attributes='',
                                context=context)
            content = format_content(content=processed_tag.content,
                                     format_func='html_fmt', level=level + 1)

            attributes = self.attributes.copy()
            attributes['class'] = 'ref'

            # setup the url path and include the anchor if the label is not
            # for a DocumentLabel. DocumentLabels should just point to the
            # file itself.
            include_anchor = not isinstance(label, DocumentLabel)
            attributes['href'] = self.url(include_html_anchor=include_anchor)

            # wrap content in 'a' tag
            return html_tag('a', attributes=attributes,
                            formatted_content=content,
                            level=level,
                            pretty_print=False)  # no line breaks
        else:
            return ''
