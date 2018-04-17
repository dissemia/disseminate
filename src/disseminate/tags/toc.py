"""
Formatting of Table of Contents for documents
"""
from itertools import groupby

from lxml.builder import E
from lxml import etree

from .headings import toc_levels as heading_toc_levels
from ..attributes import get_attribute_value, remove_attribute
from ..tags.headings import Chapter
from .core import Tag
from .. import settings


class TocError(Exception):
    """An error was encountered while processing a table of contents tag."""
    pass


def process_context_toc(context, target):
    """Process a the 'toc' in the context by replacing it with a toc string.

    A 'toc' field may optionally be placed in the context of a document.
    If present, this function will read in the options for the 'toc' field and
    return a string for the given target.

    Parameters
    ----------
    context : dict
        The context dict containing values for the document.
    target : str
        The target (extension) for the output TOC. ex: '.html', '.tex'
    """
    # Get the toc kind from the context and store it in the 'toc_kind' entry
    if 'toc_kind' in context:
        toc_kind = context['toc_kind']
    else:
        if 'toc' in context:
            toc_kind = context['toc']
            context['toc_kind'] = toc_kind
        else:
            return None
    attributes = tuple()

    # Create the tag
    toc = Toc(name='toc', content=toc_kind, attributes=attributes,
              context=context)

    # Render the toc
    target_stripped = (target if not target.startswith('.') else
                       target[1:])
    render_func = getattr(toc, target_stripped, None)

    if render_func is not None and callable(render_func):
        result = render_func()
        if target == '.html':
            # For the '.html' target, the element tree has to be converted
            # to an html string
            html = etree.tostring(result, pretty_print=True).decode('utf-8')
            context['toc'] = html
        else:
            context['toc'] = result
    else:
        context['toc'] = toc.default()


def tree_to_html(elements, context, tag='ol', level=1):
    """Convert a nested tree to html"""
    returned_elements = []
    for e in elements:
        if isinstance(e, tuple) and len(e) == 2:
            # Unpack the element if it's a tuple with the order and the element
            order, e = e
        if isinstance(e, list):
            returned_elements.append(tree_to_html(e, context, tag, level+1))
        else:
            kwargs = {'class': 'li-' + e.kind[-1] if e.kind else ''}
            returned_elements.append(E('li', e.ref(target='.html'),
                                       **kwargs))

    kwargs = {'class': 'toc-level-' + str(level)}
    return E(tag, *returned_elements, **kwargs)


def tree_to_tex(elements, context, level=1,
                listing=settings.toc_listing,
                pageref_width=settings.toc_pageref_width,
                bolded_kinds=settings.toc_bolded_kinds,
                dotted_kinds=settings.toc_dotted_kinds):
    """Convert a nested tree to tex.

    Parameters
    ----------
    elements : list of :obj:`disseminate.labels.Label`
        A nested list of label objects.
    context : dict
        The document's context dict.
    level : int, optional
        The toc entry level, starting at 1.
    listing : str, optional
        The type of latex list environment to use.
    pageref_width : str, optional
        The width reserved for the page number in the pageref
    bolded_kinds : tuple of str, optional
        These entries will be bolded.
    dotted_kinds : tuple of str, optional
        When placing the pageref of latex entries, either an \hfill or \dotfill
        is used. The \dotfill will be used for labels of the given kind.
    """
    returned_elements = []
    for e in elements:
        if isinstance(e, tuple) and len(e) == 2:
            # Unpack the element if it's a tuple with the order and the element
            order, e = e
        if isinstance(e, list):
            returned_elements.append(tree_to_tex(e, context, level+1))
        else:
            # Prepare the entry
            entry = "  " * level
            entry += "\\item "
            if e.kind[-1] in bolded_kinds:
                entry += "\\textbf{"
            entry += e.ref(target='.tex')
            entry += (" \\dotfill " if e.kind[-1] in dotted_kinds
                      else " \\hfill ")
            entry += "\\makebox[" + pageref_width + "][r]{"
            entry += e.pageref(target='.tex')
            entry += "}"
            if e.kind[-1] in bolded_kinds:
                entry += "}"
            entry += "\n"

            returned_elements.append(entry)

    if returned_elements:
        return ("  " * (level - 1) + "\\begin{{{}}}\n".format(listing) +
                ''.join(returned_elements) +
                "  " * (level - 1) + "\\end{{{}}}\n".format(listing))
    else:
        return ''


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
    header_tag = None

    def __init__(self, name, content, attributes, context):
        super(Toc, self).__init__(name, content, attributes, context)

        # Get the TOC's kind from the tag's content
        self.toc_kind = (self.content.strip() if isinstance(self.content, str)
                         else '')

        # Setup the TOC header, if specified
        header = get_attribute_value(self.attributes, 'header')
        self.attributes = remove_attribute(self.attributes, 'header')

        if header is not None:
            self.header_tag = Chapter(name='TOC', content='Table of Contents',
                                      attributes=('nolabel',), context=context)

    def construct_tree(self, labels, order_function):
        """Construct a toc tree for the given target.

        Parameters
        ----------
        labels : list of :obj:`disseminate.labels.Label`
           The labels to construct a tree from.
        order_function : :function:
            A function which returns the order of a given label item. The
            function takes a label and returns an integer. The base TOC levels
            start at 0, and the sub-levels return higher numbers.
        target : str
            The target for the tree to construct.
            ex: '.html', '.tex' or None (for default)
        """
        # Get the label_manager and labels
        elements = []

        # Got through the labels and keep track of the heading levels
        max_level = 0
        for label in labels:
            try:
                level = order_function(label)
            except ValueError:
                level = 0

            if level > max_level:
                max_level = level

            # Create the item
            elements.append((level, label))

        # Group the levels
        for level in reversed(range(0, max_level)):
            groups = [(k, list(g)) for k, g in
                      groupby(elements, lambda x: x[0] > level)]

            elements = []
            for above_level, g in groups:
                if above_level is False:
                    # These are smaller than the current level. Do not
                    # group these values and add them back to the list
                    elements += list(g)
                else:
                    # These are as large as the current level. Group them
                    # in their own sub-list
                    elements.append((level, [j[1] for j in g]))

        return elements

    def get_labels(self):
        """Get the labels, ordering function and labeling type."""
        current_document = self.context.get('document', None)

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

    def html(self, level=1):
        """Convert the tag to an html listing.

        .. note:: The 'document' toc is special since it uses the documents
                  directly to construct the tree. All other toc types will
                  get the labels from the label_manager

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        labels, order_function, heading_type = self.get_labels()

        if len(labels) > 0:
            elements = self.construct_tree(labels=labels,
                                           order_function=order_function)
            html = tree_to_html(elements=elements, context=self.context)

            # Add the class to the HTML element
            if heading_type:
                html.attrib['class'] = 'toc-' + heading_type

            if self.header_tag is not None:
                html = [self.header_tag.html(level+1), html]
        else:
            html = ''

        return html

    def tex(self, level=1, mathmode=False):
        """Convert the tag to a tex listing.

        .. note:: The 'document' toc is special since it uses the documents
                  directly to construct the tree. All other toc types will
                  get the labels from the label_manager

        Returns
        -------
        tex : str
            A string in TEX format
        """
        labels, order_function, heading_type = self.get_labels()

        if len(labels) > 0:
            elements = self.construct_tree(labels=labels,
                                           order_function=order_function)
            tex = tree_to_tex(elements=elements, context=self.context)

            if self.header_tag is not None:
                tex = self.header_tag.tex(level+1) + tex
        else:
            tex = ''

        return tex
