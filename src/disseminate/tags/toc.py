"""
Formatting of Table of Contents for documents
"""
from .headings import toc_levels as heading_toc_levels, Heading
from .ref import Ref
from .tag import Tag
from . import exceptions
from ..formats import xhtml_tag, xhtml_list


class TocError(Exception):
    """An error was encountered while processing a table of contents tag."""
    pass


class TocRef(Ref):
    """A Ref tag for the TOC.

    This is a separate class so that the label_fmt may be different for TOC
    entries.
    """
    # The tocref tag should not be accessible on its own; it is created
    # by the Toc tag
    active = False

    html_name = "li"

    def tex_fmt(self, content=None, attributes=None, mathmode=False,
                cache=None, level=1, **kwargs):
        list_level = self.attributes['level']
        tex_content = super().tex_fmt(content=content, attributes=attributes,
                                      mathmode=mathmode, cache=cache,
                                      level=level, **kwargs)
        return "§" * list_level + " " + tex_content + "\n"

    def html_fmt(self, content=None, attributes=None, cache=None,
                 format_func='html_fmt', method='html', level=1, **kwargs):
        # Wrap the tocref item in a list item
        html = super().html_fmt(content=content, attributes=attributes,
                                cache=cache, format_func=format_func,
                                method=method, level=level)

        tag_class = ('class="toc-level-{}"'.format(self.attributes['level'])
                     if 'level' in self.attributes else '')
        return xhtml_tag('li', formatted_content=html, attributes=tag_class,
                         method=method)


class Toc(Tag):
    """Table of contents and listings.

    contents : str
        The contents are the label types to list. The following entries
        are supported:

        - document: list the document labels
        - heading : list heading labels
        - figure : list figure labels
        - table : list table labels

        Additionally, the following modifiers have special meaning:
        - all : list labels from all documents
        - current : list labels from the current document (default)


        - expanded : pertains to 'all document' and 'all headings'.
                     Show all label references for all documents.
        - abbreviated : pertains to 'all document' and 'all headings'.
                        show all label references for the current document and
                        the top level heading for other documents.
        - collapsed : pertains to 'all document' and 'all headings'.
                     show only the documents without headings. (default)
    """

    active = True
    toc_kind = None
    toc_elements = None
    header_tag = None

    tex_env = "easylist"
    list_style = 'booktoc'
    html_name = 'ol'

    process_typography = False

    _ref_tags = None

    def __init__(self, name, content, attributes, context):
        super(Toc, self).__init__(name, content, attributes, context)

        # Get the TOC's kind from the tag's content
        content = self.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0]
        if isinstance(content, str):
            self.toc_kind = content.split()
        elif isinstance(content, Tag):
            self.toc_kind = content.txt

        # If the TOC kind hasn't been assigned, the content could not be
        # parsed. Raise an exception
        if self.toc_kind is None:
            msg = "The {} tag could not parse the tag contents: {}"
            raise exceptions.TagError(msg.format(self.name, content))

        # Setup the TOC header, if specified
        header = self.attributes.pop('header', None)

        if header is not None:
            self.header_tag = Heading(name='TOC', content='Table of Contents',
                                      attributes='nolabel', context=context)

    def get_labels(self):
        """Get the labels, ordering function and labeling type.

        Returns
        -------
        labels : List[:obj:`.label_manager.types.Label`]
            The labels referenced by this TOC.
        """
        assert self.context.is_valid('label_manager')

        # If 'all' is specified in the toc_kind, then all documents should be
        # selected. This is done by having a doc_id of None with the
        # 'get_labels_by_kind' method of the label manager. If 'all' is not
        # specified, then use this document's doc_id. This will return labels
        # only for this document and its context from the 'get_labels_by_kind'
        # method of the label manager.
        context = self.context
        doc_id = context.get('doc_id') if 'all' not in self.toc_kind else None
        label_manager = self.context['label_manager']

        labels = []
        if 'heading' in self.toc_kind or 'headings' in self.toc_kind:
            labels += label_manager.get_labels_by_kind(doc_id=doc_id,
                                                       kinds='heading')
        if 'document' in self.toc_kind or 'documents' in self.toc_kind:
            labels += label_manager.get_labels_by_kind(doc_id=doc_id,
                                                       kinds='document')

        # Now filter apply additional filters
        doc_id = context.get('doc_id')
        if 'abbreviated' in self.toc_kind:
            current_doc_id = None
            filtered_labels = []

            for label in labels:
                if label.doc_id == doc_id:
                    # This is a label for the current document keep it
                    filtered_labels.append(label)
                elif label.doc_id != current_doc_id:
                    # This is a label for a different document. Only keep it
                    # if it's the first label for this other document
                    filtered_labels.append(label)
                current_doc_id = label.doc_id

            # Transfer the filtered list
            labels.clear()
            labels += filtered_labels

        return labels

    @property
    def reference_tags(self):
        """This tag's TocRef tag items.
        """
        labels = self.get_labels()

        # Collect the created tags.
        tags = []

        # Got through the labels and keep track of the levels
        current_level = 1
        for label in labels:
            # Get the level for the label
            if label.kind[-1] in heading_toc_levels:
                level = heading_toc_levels.index(label.kind[-1])
            else:
                level = current_level
            current_level = level

            # Create the tag and add it to the tags list
            tag_name = 'toc-' + label.kind[-1]
            tag = TocRef(name=tag_name, content=label.id,
                         attributes=self.attributes, context=self.context)
            tag.attributes['level'] = level

            tags.append(tag)

        return tags

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        tags = list(self.reference_tags)
        tags[0:0] = "\\ListProperties(Hide=2)\n"  # Add to front
        return super().tex_fmt(content=tags, attributes=self.list_style)

    def html_fmt(self, content=None, attributes=None, cache=None,
                 format_func='html_fmt', method='html', level=1, **kwargs):
        tags = self.reference_tags
        elements = []

        root_document = self.context.root_document
        documents_by_id = (root_document.documents_by_id(recursive=True)
                           if root_document is not None else None)

        # Get the labels
        labels = self.get_labels()
        labels_by_id = {label.id: label for label in labels}

        for tag in tags:
            listlevel = tag.attributes['level']
            label = labels_by_id.get(tag.label_id, None)

            cache = dict() if cache is None else cache
            cache['label'] = label
            cache['documents_by_id'] = documents_by_id

            func = getattr(tag, format_func)
            tag_html = func(cache=cache, method=method, level=level + 1)
            elements.append((listlevel, tag_html))

        return xhtml_list(*elements, attributes='class="toc"',
                          listtype=self.html_name, method=method, level=level)
