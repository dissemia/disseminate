"""
Navigation tags
"""
import weakref
from os.path import relpath
from itertools import groupby

from .tag import Tag
from .ref import Ref
from ..signals import signal
from ..formats import html_tag

document_tree_updated = signal('document_tree_updated')


@document_tree_updated.connect_via(order=10000)
def set_navigation_labels(root_document):
    """Set the navigation labels in the context of all documents in a document
    tree."""
    root_context = root_document.context
    assert root_context.is_valid('label_manager')

    # Get doc_ids by target
    doc_ids_by_target = dict()
    documents = root_document.documents_list(only_subdocuments=False,
                                             recursive=True)
    for document in documents:
        targets = document.targets
        doc_id = document.doc_id

        for target in targets:
            l = doc_ids_by_target.setdefault(target, [])
            l.append(doc_id)

    # Get all of the document labels
    label_manager = root_context.get('label_manager')
    labels = label_manager.get_labels(kinds='heading')
    labels_by_doc_id = {doc_id: next(group) for doc_id, group in
                        groupby(labels, lambda l: l.doc_id)}

    # Set the prev_labels and next_labels entries in the context of each
    # document
    for target in targets:
        if target not in doc_ids_by_target:
            continue
        doc_ids = doc_ids_by_target[target]

        for document in documents:
            doc_id = document.doc_id

            # Find this document's doc_id in the doc_ids_by_target
            try:
                position = doc_ids.index(doc_id)
            except ValueError:
                position = None

            # See if the prev, next, curr links are avalaiable
            for name, rel in (('prev', - 1), ('curr', 0), ('next', 1)):

                # Don't use back-tracking indexes
                rel_position = position + rel if position is not None else None
                rel_position = (None if rel_position is None or
                                rel_position < 0 else rel_position)
                key = "_".join((name, target.strip('.')))
                try:
                    other_doc_id = doc_ids[rel_position]
                    other_label = labels_by_doc_id[other_doc_id]
                    document.context[key] = weakref.ref(other_label)
                except (IndexError, KeyError, TypeError):
                    # If the other document could not be found, make sure this
                    # entry isn't in the context. This can happen if the context
                    # contains stale information from a previous invocation of
                    # this function.

                    if key in document.context:
                        del document.context[key]


class Next(Ref):
    """Produces links to the next document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    2. The following are tag attributes that are recognized:

    kind : str
        The kind of label to reference by this tag. By default, it's a
        heading.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None, attributes=None, label=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, attributes=None, mathmode=False, label=None,
                level=1):
        context = self.context
        label = context.get('next_html', None)
        if label:
            label = label()
            return super(Next, self).html_fmt(content=content, label=label,
                                              level=level)
        else:
            return ""

    def html_fmt(self, content=None, attributes=None, label=None, level=1):
        context = self.context
        # Get the label for the next document
        label = context.get('next_html', None)
        if label:
            label = label()
            return super(Next, self).html_fmt(content=content, label=label,
                                              level=level)
        else:
            return ""


class Prev(Ref):
    """Produces links to the previous document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    2. The following are tag attributes that are recognized:

    kind : str
        The kind of label to reference by this tag. By default, it's a
        heading.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None, attributes=None, label=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, attributes=None, mathmode=False, label=None,
                level=1):
        context = self.context
        label = context.get('prev_html', None)
        if label:
            label = label()
            return super(Prev, self).html_fmt(content=content, label=label,
                                              level=level)
        else:
            return ""

    def html_fmt(self, content=None, attributes=None, label=None, level=1):
        context = self.context
        # Get the label for the next document
        label = context.get('prev_html', None)
        if label:
            label = label()
            return super(Prev, self).html_fmt(content=content, label=label,
                                              level=level)
        else:
            return ""


class Pdflink(Ref):
    """Produces a link to the pdf for this document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    """

    active = True

    def __init__(self, name, content, attributes, context):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name, content, attributes, context)

    def default_fmt(self, content=None, attributes=None, label=None):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, content=None, attributes=None, mathmode=False, label=None,
                level=1):
        # The next reference is designed for html only
        return ""

    def html_fmt(self, content=None, attributes=None, label=None, level=1):
        context = self.context
        
        # Only works if the document that owns this tag will be rendered to
        # a pdf.
        if '.pdf' not in context.targets:
            return ""

        # Get the document that owns this context and reconstruct the link to
        # the pdf.
        document = context.document
        pdf_target_filepath = document.target_filepath('.pdf')
        html_target_filepath = document.target_filepath('.html')

        # Get the relative path do this html document
        relative_path = relpath(pdf_target_filepath, html_target_filepath)

        attrs = self.attributes.copy() if attributes is None else attributes
        attrs['class'] = 'ref'
        attrs['href'] = relative_path

        # wrap content in 'a' tag
        return html_tag('a', attributes=attrs,
                        formatted_content='pdf',
                        level=level,
                        pretty_print=False)  # no line breaks

