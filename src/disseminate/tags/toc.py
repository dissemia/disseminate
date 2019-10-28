"""
Formatting of Table of Contents for documents
"""
from .headings import toc_levels as heading_toc_levels, Heading
from .ref import Ref
from .tag import Tag
from . import exceptions
from ..formats import html_tag, html_list, tex_env


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

    def html_fmt(self, content=None, attributes=None, label=None, level=1):
        # Wrap the tocref item in a list item
        html = super().html_fmt(content=content, attributes=attributes,
                                label=label, level=level)
        tag_class = ('class="toc-level-{}"'.format(self.attributes['level'])
                     if 'level' in self.attributes else '')
        return html_tag('li', formatted_content=html, attributes=tag_class)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, label=None,
                level=1):
        list_level = self.attributes['level']
        tex_content = super().tex_fmt(content=content, attributes=attributes,
                                      mathmode=mathmode, label=label,
                                      level=level)
        return "§" * list_level + " " + tex_content + "\n"


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
    html_name = 'ul'

    process_typography = False

    _mtime = None
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

        # If the TOC kind hasn't been assigned, the content could be parsed.
        # Raise and exception
        if self.toc_kind is None:
            msg = "The {} tag could not parse the tag contents: {}"
            raise exceptions.TagError(msg.format(self.name, content))

        # Setup the TOC header, if specified
        header = self.attributes.pop('header', None)

        if header is not None:
            self.header_tag = Heading(name='TOC', content='Table of Contents',
                                      attributes='nolabel', context=context)

    @property
    def mtime(self):
        # Get the maximum mtimes from the labels this toc tag depends on
        labels = self.get_labels()
        label_mtimes = [label.mtime for label in labels]
        mtimes = list(filter(bool, label_mtimes + [self._mtime]))
        return max(mtimes) if mtimes else None

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
        # 'get_labels' method of the label manager. If 'all' is not
        # specified, then use this document's doc_id. This will return labels
        # only for this document and its context from the 'get_labels' method
        # of the label manager.
        context = self.context
        doc_id = context.get('doc_id') if 'all' not in self.toc_kind else None
        label_manager = self.context['label_manager']

        labels = []
        if 'heading' in self.toc_kind or 'headings' in self.toc_kind:
            labels += label_manager.get_labels(doc_id=doc_id, kinds='heading')
        if 'document' in self.toc_kind or 'documents' in self.toc_kind:
            labels += label_manager.get_labels(doc_id=doc_id, kinds='document')

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
        # Get labels and determine their latest modification time (mtime).
        # We poll the fresh list of labels instead of the cached ref_tags
        # because the entries in the TOC may have changed since the ref_tags
        # were last loaded.
        labels = self.get_labels()
        label_mtimes = [label.mtime for label in labels]
        latest_mtime = max(label_mtimes) if len(label_mtimes) > 0 else None

        # Determine whether the labels are up to date and whether tags have
        # already been prepared. If so, use those.
        if (self._ref_tags is not None and
            self._mtime is not None and
            latest_mtime is not None and
           self._mtime >= latest_mtime):
            return self._ref_tags

        # The labels have changed. Update the ref tags.
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

        # Cache the ref tags and update the modification time for labels
        self._ref_tags = tags
        self._mtime = latest_mtime
        return self._ref_tags

    def html_fmt(self, content=None, attributes=None, level=1):
        tags = self.reference_tags
        elements = []

        for tag in tags:
            listlevel = tag.attributes['level']
            tag_html = tag.html_fmt(level=level + 1)
            elements.append((listlevel, tag_html))

        return html_list(*elements, attributes='class="toc"',
                         listtype=self.html_name, level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        tags = list(self.reference_tags)
        tags[0:0] = "\\ListProperties(Hide=2)\n"  # Add to front
        return super().tex_fmt(content=tags, attributes=self.list_style)
