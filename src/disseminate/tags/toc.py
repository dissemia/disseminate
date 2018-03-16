"""
Formatting of Table of Contents for documents
"""
from lxml.builder import E
from lxml import etree

from . import settings
from . import headings
from .core import Tag
from ..attributes import (get_attribute_value, filter_attributes,
                          kwargs_attributes)


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

    _heading_kinds = None

    def __init__(self, *args, **kwargs):
        super(Toc, self).__init__(*args, **kwargs)

        # Cache the heading label kinds
        if Toc._heading_kinds is None:
            Toc._heading_kinds = [cls.__name__.lower()
                                  for cls in headings.__dict__.values()
                                  if getattr(cls, 'label_heading', False)]

    def headings_html(self, document=None):
        """Construct a headings html listing for the given document."""
        # Use the current document, if None is specified
        if document is None and '_document' in self.local_context:
            document = self.local_context['_document']

        # Get the label_manager and labels
        elements = []
        if '_label_manager' in self.global_context and document is not None:
            label_manager = self.global_context['_label_manager']
            labels = label_manager.get_labels(document=document,
                                              kinds=self._heading_kinds)

            for label in labels:
                e = E('li', label.ref_html(self.local_context,
                                           self.global_context))
                elements.append(e)

        if len(elements) > 0:
            valid_attrs = settings.html_valid_attributes['ol']
            attrs = filter_attributes(attrs=self.attributes,
                                      attribute_names=valid_attrs,
                                      target='.html')
            kwargs = kwargs_attributes(attrs)

            # add a class to the tag
            if 'class' in kwargs:
                kwargs['class'] += ' toc-heading'
            else:
                kwargs['class'] = 'toc-heading'

            return E('ol', *elements, **kwargs)
        else:
            return ""

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
                    link = E('a', document.title,
                             href=document.target_filepath(target='.html',
                                                           render_path=False))
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
        assert '_label_manager' in  self.global_context
        assert '_tree' in self.global_context
        assert '_document' in self.local_context

        # Get the label manager
        label_manager = self.global_context['_label_manager']

        # Get the kind of toc and format of listing
        toc_kind = self.content.strip()

        if toc_kind.startswith('all documents'):
            element = self.documents_html()
        else:
            element = ''

        if isinstance(element, str):
            return element
        else:
            # Convert the element to a string
            return (etree.tostring(element, pretty_print=settings.html_pretty)
                         .decode("utf-8"))
