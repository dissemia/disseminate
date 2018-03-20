"""
Formatting of Table of Contents for documents
"""
from itertools import groupby

from lxml.builder import E
from lxml import etree

from . import settings
from .headings import toc_levels
from .core import Tag
from ..attributes import (get_attribute_value, filter_attributes,
                          kwargs_attributes)


class TocError(Exception):
    """An error was encountered while processing a table of contents tag."""
    pass


def process_toc(target, local_context, global_context):
    """Process a string for the 'toc' in the local_context.

    A 'toc' field may optionally be placed in the local_context of a document.
    If present, this function will read in the options for the 'toc' field and
    return a string for the given target.

    Parameters
    ----------
    target : str
        The target (extension) for the output TOC. ex: '.html', '.tex'
    local_context : dict
        The local_context dict containing values for a specific document.
    global_context : dict
        The global_context dict caintain values for a group of documents (tree).

    Returns
    -------
    toc : str
        The string for the TOC. If no 'toc' was found in the local_context, an
        empty string is returned
    """
    if 'toc' not in local_context:
        return ''

    toc_kind = (local_context['toc']['kind'] if
                'kind' in local_context['toc'] else local_context['toc'])
    toc_format = (local_context['toc']['format'] if
                  'format' in local_context['toc'] else None)

    if toc_format is not None:
        attributes = (('format', toc_format),)
    else:
        attributes = tuple

    if isinstance(toc_kind, str):
        # Create the tag
        toc = Toc(name='toc', content=toc_kind, attributes=attributes,
                  local_context=local_context, global_context=global_context)
        if target == '.html':
            return toc.html()
        else:
            # Unknown format
            return ''
    else:
        return ''


def tree_to_html(elements, local_context, global_context, tag='ol'):
    """Convert a nested tree to html"""
    returned_elements = []
    for e in elements:
        if isinstance(e, tuple) and len(e) == 2:
            # Unpack the element if it's a tuple with the order and the element
            order, e = e
        if isinstance(e, list):
            returned_elements.append(tree_to_html(e, local_context,
                                                  global_context, tag))
        else:
            returned_elements.append(E('li', e.ref(target='.html')))

    return E(tag, *returned_elements)


def tree_to_tex(elements, local_context, global_context, level=1,
                listing='enumerate'):
    """Convert a nested tree to tex."""
    returned_elements = []
    for e in elements:
        if isinstance(e, tuple) and len(e) == 2:
            # Unpack the element if it's a tuple with the order and the element
            order, e = e
        if isinstance(e, list):
            returned_elements.append(tree_to_tex(e, local_context,
                                                  global_context, level+1))
        else:
            returned_elements.append("  " * level + "\item " +
                                     e.ref(target='.tex') +
                                     "\n")

    if returned_elements:
        return ("  " * (level - 1) + "\\begin{{{}}}\n".format(listing) +
                ''.join(returned_elements) +
                "  " * (level - 1) + "\\end{{{}}}\n".format(listing))
    else:
        return ''


# def tree_to_txt

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

    toc_kind = None

    def __init__(self, *args, **kwargs):
        super(Toc, self).__init__(*args, **kwargs)

        self.toc_kind = (self.content.strip() if isinstance(self.content, str)
                         else '')

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

    def documents_html(self):
        """Construct the documents html listing."""
        # Get the format of the documents listing
        format = get_attribute_value(attrs=self.attributes,
                                     attribute_name='format')

        # Get the documents
        elements = []
        if '_tree' in self.global_context and '_document' in self.local_context:
            tree = self.global_context['_tree']
            documents = tree.get_documents()
            current_document = self.local_context['_document']

            for document in documents:
                # Get the headings for the document, if needed
                if isinstance(format, str):
                    if 'expanded' in format:
                        headings= self.headings_html(document=document)
                    elif ('abbreviated' in format and
                          document == current_document):
                        headings = self.headings_html(document=document)
                    else:
                        headings = ''
                else:
                    headings = ''

                # Process each of the documents
                if document == current_document:
                    # Treat the current document differently. It should not
                    # have a link and may contain headings
                    elements.append(E('li', document.title, headings))
                else:
                    # Create links to other documents
                    tgt = document.target_filepath(target='.html',
                                                   render_path=False)
                    tgt = '/' + tgt

                    link = E('a', document.title, href=tgt)
                    elements.append(E('li', link, headings))

        if len(elements) > 0:
            valid_attrs = settings.html_valid_attributes['ol']
            attrs = filter_attributes(attrs=self.attributes,
                                      attribute_names=valid_attrs,
                                      target='.html')
            kwargs = kwargs_attributes(attrs)

            # add a class to the tag
            if 'class' in kwargs:
                kwargs['class'] += ' toc-document'
            else:
                kwargs['class'] = 'toc-document'

            return E('ol', *elements, **kwargs)
        else:
            return ""

    def get_labels(self):
        """Get the labels, ordering function and labeling type."""
        def default_order_function(label):
            return 0

        default_return_value = [], default_order_function, ''

        if '_label_manager' in self.global_context:
            label_manager = self.global_context['_label_manager']
        else:
            return default_return_value

        if 'heading' in self.toc_kind:
            labels = label_manager.get_labels(kinds='heading')

            def order_function(label):
                return toc_levels.index(label.kind[-1])

            return labels, order_function, 'heading'
        if 'document' in self.toc_kind:
            # Get the documents and tree
            if ('_tree' not in self.global_context or
               '_document' not in self.local_context):
                return default_return_value

            tree = self.global_context['_tree']
            documents = tree.get_documents()
            current_document = self.local_context['_document']

            # Get the labels
            labels = []
            for document in documents:
                # Get the document's label
                doc_labels = label_manager.get_labels(document=document,
                                                      kinds='document')

                if len(doc_labels) != 1:
                    # Only one label for the document should have been returned
                    continue
                labels += doc_labels

                # Get the labels for the headings for the document, if needed
                if ('expanded' in self.toc_kind or
                   ('abbreviated' in self.toc_kind and
                    document == current_document)):

                    labels += label_manager.get_labels(document=document,
                                                       kinds='heading')

            # Create and order function that includes documents
            doc_levels = ('document',) + toc_levels

            def order_function(label):
                return doc_levels.index(label.kind[-1])

            return labels, order_function, 'document'
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
            html = tree_to_html(elements=elements,
                                local_context=self.local_context,
                                global_context=self.global_context)

            # Add the class to the HTML element
            if heading_type:
                html.attrib['class'] = 'toc-' + heading_type
        else:
            html = ''

        if isinstance(html, str):
            return html
        else:
            # Convert the element to a string
            return (etree.tostring(html, pretty_print=settings.html_pretty)
                         .decode("utf-8"))

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
            tex = tree_to_tex(elements=elements,
                              local_context=self.local_context,
                              global_context=self.global_context)
        else:
            tex = ''

        return tex
