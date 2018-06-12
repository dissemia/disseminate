"""
Formatting of Table of Contents for documents
"""
from itertools import groupby

from lxml.builder import E
from lxml import etree

from .headings import toc_levels as heading_toc_levels
from .caption import Ref
from .core import Tag
from ..tags.headings import Heading
from .. import settings


class TocError(Exception):
    """An error was encountered while processing a table of contents tag."""
    pass


class Toc(Tag):
    """Table of contents and listings.

    contents : str
        The contents are the label types to list. ex: 'document', 'figure'

    attributes : tuple
        - For 'all documents' TOCs, the following attributes modify the
          behavior:
            - 'format': 'expanded' -- show all documents are including all
                         headings.
            - 'format': 'abbreviated' -- show all documents but only show
                         headings for the current document.
            - 'format': 'collapsed' -- show only the documents without headings.
                        (default)
    """

    active = True
    toc_kind = None
    toc_elements = None
    header_tag = None

    _mtime = None
    ref_tags = None

    def __init__(self, name, content, attributes, context):
        super(Toc, self).__init__(name, content, attributes, context)

        # Get the TOC's kind from the tag's content
        self.toc_kind = (self.content.strip() if isinstance(self.content, str)
                         else '')

        # Setup the TOC header, if specified
        header = self.get_attribute(name='header', clear=True)

        if header is not None:
            self.header_tag = Heading(name='TOC', content='Table of Contents',
                                      attributes=('nolabel',), context=context)

    def get_labels(self):
        """Get the labels, ordering function and labeling type."""
        # Get the document from the context, which is a weakref to the document
        current_document = self.context.get('document', None)
        current_document = (current_document() if current_document is not None
                            and callable(current_document) else None)

        def default_order_function(label):
            return 0

        default_return_value = [], default_order_function, ''

        if 'label_manager' in self.context:
            label_manager = self.context['label_manager']
        else:
            return default_return_value

        if 'heading' in self.toc_kind:
            document = current_document if 'all' not in self.toc_kind else None
            labels = label_manager.get_labels(document=document,
                                              kinds='heading')

            last_heading_level = None
            current_toc_level = 0

            # Setup the ordering function. This ordering function is setup so
            # that the heading level only increases or decreases by 1 level at
            # a time. The is because the heading level may jump by 2 or more
            # levels (ex: heading -> subsubheading), and this can trip up
            # enumerate environments for targets like tex.
            def order_function(label):
                nonlocal last_heading_level
                nonlocal current_toc_level
                heading_level = heading_toc_levels.index(label.kind[-1])

                if last_heading_level is None:  # Start at base level
                    current_toc_level = 0
                elif heading_level > last_heading_level:  # Increase level
                    current_toc_level += 1
                elif heading_level < last_heading_level:  # Decrease level
                    current_toc_level -= 1
                last_heading_level = heading_level
                return current_toc_level

            return labels, order_function, 'heading'

        if 'document' in self.toc_kind:
            document = current_document if 'all' not in self.toc_kind else None

            # Get the labels for the documents and the headings
            document_labels = label_manager.get_labels(document=document,
                                                       kinds='document')
            heading_labels = label_manager.get_labels(document=document,
                                                      kinds='heading')

            # Reorganize the document and heading labels such that the headings
            # are between documents
            merged_labels = []
            for document_label in document_labels:
                merged_labels.append(document_label)

                # Add the headings either if this is an 'expanded' toc, or
                # it's an 'abbreviated' toc, but the document corresponds to the
                # current document
                if ('expanded' in self.toc_kind or
                   ('abbreviated' in self.toc_kind and
                    document_label.document == current_document)):

                    merged_labels += [l for l in heading_labels
                                      if l.document == document_label.document]

            # Get a toc_levels for the document, based on the document_labels
            doc_toc_levels = {l.kind[-1] for l in document_labels}
            doc_toc_levels = tuple(sorted(doc_toc_levels))
            merged_toc_levels = doc_toc_levels + heading_toc_levels

            last_doc_level = None
            current_toc_level = 0

            # Setup the ordering function. This ordering function is setup so
            # that the document and heading  level only increases or decreases
            # by 1 level at a time. The is because the document or heading
            # level may jump by 2 or more levels (ex: heading -> subsubheading),
            # and this can trip up enumerate environments for targets like tex.
            def order_function(label):
                nonlocal last_doc_level
                nonlocal current_toc_level
                specific_kind = label.kind[-1]
                doc_level = merged_toc_levels.index(specific_kind)

                if last_doc_level is None:  # Start at the base level
                    current_toc_level = 0
                elif doc_level > last_doc_level:  # Increase by 1 level
                    current_toc_level += 1
                elif doc_level < last_doc_level:  # Decrease by 1 level
                    current_toc_level -= 1
                last_doc_level = doc_level
                return current_toc_level

            return merged_labels, order_function, 'document'

        else:
            return default_return_value

    def update_tags(self):
        """Populate this tag's content by adding TocRef items.

        Parameters
        ----------
        labels : list of :obj:`disseminate.labels.Label`
           The labels to construct a tree from.
        order_function : :function:
            A function which returns the order of a given label item. The
            function takes a label and returns an integer. The base TOC levels
            start at 0, and the sub-levels return higher numbers.
        """
        # Get labels and determine their latest modification time (mtime).
        # We poll the fresh list of labels instead of the cached ref_tags
        # because the entries in the TOC may have changed since the ref_tags
        # were last loaded.
        labels, order_function, heading_type = self.get_labels()
        label_mtimes = [label.mtime for label in labels]
        latest_mtime = max(label_mtimes) if len(label_mtimes) > 0 else None

        # Determine whether the labels are up to date and whether tags have
        # already been prepared. If so, use those.
        if (self.ref_tags is not None and
            self._mtime is not None and
            latest_mtime is not None and
           self._mtime >= latest_mtime):
            return self.ref_tags

        # The labels have changed. Update the ref tags.
        # Collect the created tags.
        tags = []

        # Got through the labels and keep track of the heading levels
        max_level = 0
        for label in labels:
            try:
                level = order_function(label)
            except ValueError:
                level = 0

            if level > max_level:
                max_level = level

            # Create the tag and add it to the tags list
            tag_name = 'toc-' + label.kind[-1]
            tag = Ref(name=tag_name, content=label.id,
                      attributes=self.attributes, context=self.context)

            # Add the tag to a flat list
            tags.append((level, tag))

        # Group the levels
        for level in reversed(range(0, max_level)):
            groups = [(k, list(g)) for k, g in
                      groupby(tags, lambda x: x[0] > level)]

            tags = []
            for above_level, g in groups:
                if above_level is False:
                    # These are smaller than the current level. Do not
                    # group these values and add them back to the list
                    tags += list(g)
                else:
                    # These are as large as the current level. Group them
                    # in their own sub-list
                    tags.append((level, [j[1] for j in g]))

        # Cache the ref tags and update the modification time for labels
        self.ref_tags = tags
        self._mtime = latest_mtime

    def html(self, level=1, content=None, elements=None, listtype='ul'):
        """Convert the tag to an html listing.

        .. note:: The 'document' toc is special since it uses the documents
                  directly to construct the tree. All other toc types will
                  get the labels from the label_manager

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        # Update the ref tags, if it's the root invocation--i.e. an elements
        # list hasn't been passed by this function to itself.
        if elements is None:
            self.update_tags()

        # Get the content. It should be a list of TocRef tags.
        content = content if content is not None else self.ref_tags
        elements = elements if elements is not None else content

        if elements is None:
            return ''

        if not hasattr(elements, '__iter__'):
            elements = [elements]

        returned_elements = []
        for e in elements:

            if isinstance(e, tuple) and len(e) == 2:
                # Unpack the element if it's a tuple with the order and the
                # element
                order, e = e

            if isinstance(e, list):
                # The element is a list of tags. Process this list as a group.
                returned_elements.append(self.html(level+1, content=None,
                                                   elements=e))
            else:
                # Otherwise it's a ref tag, get its html and wrap it in a list
                # item
                returned_elements.append(E('li', e.html(level+1)))

        kwargs = {'class': 'toc-level-' + str(level)}
        e = E(listtype, *returned_elements, **kwargs)

        # Render the root tag if this is the first level
        if level == 1:
            return (etree
                .tostring(e, pretty_print=settings.html_pretty)
                .decode("utf-8"))
        else:
            return e

    def tex(self, level=1, mathmode=False, content=None, elements=None,
            listtype='toclist'):
        """Convert the tag to a tex listing.

        .. note:: The 'document' toc is special since it uses the documents
                  directly to construct the tree. All other toc types will
                  get the labels from the label_manager

        Returns
        -------
        tex : str
            A string in TEX format
        """
        # Update the ref tags, if it's the root invocation--i.e. an elements
        # list hasn't been passed by this function to itself.
        if elements is None:
            self.update_tags()

        # Get the content. It should be a list of TocRef tags.
        content = content if content is not None else self.ref_tags
        elements = elements if elements is not None else content

        if elements is None:
            return ''

        if not hasattr(elements, '__iter__'):
            elements = [elements]

        returned_elements = []
        for e in elements:

            if isinstance(e, tuple) and len(e) == 2:
                # Unpack the element if it's a tuple with the order and the
                # element
                order, e = e

            if isinstance(e, list):
                # The element is a list of tags. Process this list as a group.
                returned_elements.append(self.tex(level + 1, content=None,
                                                   elements=e))
            else:
                # Otherwise it's a ref tag, get its tex and wrap it in a list
                # item
                entry = "  " * level
                entry += "\\item " + e.tex(level + 1)


                # Format the page numbers
                entry += (" \\dotfill " if True
                          else " \\hfill ")
                #entry += "\\makebox[" + pageref_width + "][r]{"
                entry += e.tex(level + 1, page=True)

                entry += '\n'

                returned_elements.append(entry)

        if returned_elements:
            return ("  " * (level - 1) + "\\begin{{{}}}\n".format(listtype) +
                    ''.join(returned_elements) +
                    "  " * (level - 1) + "\\end{{{}}}\n".format(listtype))
        else:
            return ''