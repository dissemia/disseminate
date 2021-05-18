"""
Navigation tags
"""
import weakref
from os.path import relpath
from itertools import groupby

from markupsafe import escape

from .tag import Tag
from .ref import Ref
from ..signals import signal


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
            lst = doc_ids_by_target.setdefault(target, [])
            lst.append(doc_id)

    # Get all of the document labels
    label_manager = root_context.get('label_manager')
    labels = label_manager.get_labels_by_kind(kinds='heading')
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
                    # entry isn't in the context. This can happen if the
                    # context contains stale information from a previous
                    # invocation of this function.

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

    def __init__(self, name, content, **kwargs):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name=name, content=content, **kwargs)

    def default_fmt(self, **kwargs):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, cache=None, **kwargs):
        context = self.context
        cache = dict() if cache is None else cache

        if 'label' not in cache and 'next_tex' in context:
            label = context['next_tex']
            cache['label'] = label()  # Dereference. See above.

        if 'label' in cache:
            return super(Next, self).html_fmt(cache=cache, **kwargs)
        else:
            return ""

    def html_fmt(self, cache=None, **kwargs):
        context = self.context
        cache = dict() if cache is None else cache

        if 'label' not in cache and 'next_html' in context:
            label = context['next_html']
            cache['label'] = label()  # Dereference. See above.

        if 'label' in cache:
            return super(Next, self).html_fmt(cache=cache, **kwargs)
        else:
            return ""

    def xhtml_fmt(self, **kwargs):
        raise NotImplementedError


class Prev(Ref):
    """Produces links to the previous document.

    Notes
    -----
    1. As opposed to the parent Ref tag, if a label is not found, an empty
       string is returned by the target format functions.
    2. The following are tag attributes that are recognized

    kind : str
        The kind of label to reference by this tag. By default, it's a
        heading.
    """

    active = True

    def __init__(self, name, content, **kwargs):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name=name, content=content, **kwargs)

    def default_fmt(self, **kwargs):
        # The next reference is designed for html only
        return ""

    def tex_fmt(self, cache=None, **kwargs):
        context = self.context
        cache = dict() if cache is None else cache

        if 'label' not in cache and 'prev_tex' in context:
            label = context['prev_tex']
            cache['label'] = label()  # Dereference. See above.

        if 'label' in cache:
            return super(Prev, self).html_fmt(cache=cache, **kwargs)
        else:
            return ""

    def html_fmt(self, cache=None, **kwargs):
        context = self.context
        cache = dict() if cache is None else cache

        if 'label' not in cache and 'prev_html' in context:
            label = context['prev_html']
            cache['label'] = label()  # Dereference. See above.

        if 'label' in cache:
            return super(Prev, self).html_fmt(cache=cache, **kwargs)
        else:
            return ""

    def xhtml_fmt(self, **kwargs):
        raise NotImplementedError


class OtherLink(Tag):
    """Produces a link to a source document or another target for this
    document."""

    active = False
    other_target = None

    def __init__(self, name, content, **kwargs):
        # Bypass the Ref initiator, as it sets the label_id
        # Do not use the tag contents--this tag cannot do anything with it.
        content = ''
        Tag.__init__(self, name, content, **kwargs)

    def this_filepath(self, target):
        """The filepath for this (target) document."""
        context = self.context

        if (context is not None and target is not None and
           target in context.targets):
            return context.target_filepath(target)
        else:
            return None

    def other_filepath(self, target=None):
        """The filepath for the other document target or src_filepath to create
        a link to."""
        context = self.context
        target = target or self.other_target

        if (context is not None and target is not None and
           target in context.targets):
            return context.target_filepath(target)
        else:
            return None

    def other_relpath(self, this_target, other_target=None):
        """Produce the the relpath for the other target."""
        # Get the filepaths
        this_filepath = self.this_filepath(target=this_target)
        other_filepath = self.other_filepath(target=other_target)

        if this_filepath is None or other_filepath is None:
            # Both paths should be found to forumate a relative path
            return ''

        if this_filepath == other_filepath:
            # If both paths are the same, the relpath is the current dir,
            # and this should not give a link to itself.
            return ''

        # Generate the relative path
        rp = relpath(other_filepath, this_filepath.parent)
        return escape(rp)

    def default_fmt(self, **kwargs):
        return ""

    def tex_fmt(self, **kwargs):
        return self.other_relpath(this_target='.tex')

    def html_fmt(self, **kwargs):
        return self.other_relpath(this_target='.html')

    def xhtml_fmt(self, **kwargs):
        raise NotImplementedError


class Srclink(OtherLink):
    """Produces a link to the src file for this document"""
    active = True

    def other_filepath(self, target=None):
        context = self.context
        return (context['src_filepath'] if context is not None and
                'src_filepath' in context else None)


class Txtlink(OtherLink):
    """Produces a link to the txt target for this document."""
    active = True
    other_target = '.txt'


class Texlink(OtherLink):
    """Produces a link to the tex target for this document."""
    active = True
    other_target = '.tex'


class Pdflink(OtherLink):
    """Produces a link to the pdf target for this document"""
    active = True
    other_target = '.pdf'


class Epublink(OtherLink):
    """Produces a link to the epub target for the root document."""
    active = True
    other_target = '.epub'

    def other_filepath(self, target=None):
        context = self.context
        root_doc = getattr(context, 'root_document', None)
        root_context = root_doc.context if root_doc is not None else None

        if root_context is not None and '.epub' in root_context.targets:
            return root_context.target_filepath('.epub')
        else:
            return None
