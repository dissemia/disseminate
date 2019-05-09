"""
The label base class for the label manager.
"""


class Label(object):
    """A label used for referencing.

    Labels keep track of modification times (mtimes). The mtime may be updated
    if it's later than the mtime of the document that owns the label_manager
    that owns this label.

    The mtimes are tracked because updates to labels may require an
    update of a rendered document. For example, a project may have two
    documents, each owning a label. If the first document (and its label) is
    updated, and the second document depends on this label, then the second
    document should be re-rendered if the label has changed. However, if that
    label hasn't changed, then the second document should not be re-rendered.

    Alternatively, a label, like a chapter label, owned by a document that has
    not changed might get reordered, and its mtime should be later than the
    source document's mtime. This will trigger a re-rendering of the document.

    Parameters
    ----------
    doc_id : str
        The unique identifier (for documents within a label manager) for the
        document that owns the label.
    id : str
        The unique identifier(s) of the label. ex: 'nmr_introduction'. This
        should be unique for the entire project.
    kind : Tuple[str]
        The kind of the label is a tuple that identifies the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'chapter',)
    mtime : Optional[float]
        The modification time of the source document that created this label,
        or the modification time for changes to the label.
    order : Optional[Tuple[int]]
        The order/number of the label. The order is a tuple of integers with a
        length that matches the 'kind' tuple. Each entry represents the
        order/number of each kind  ex: for a kind ('heading', 'chapter') could
        have an order of (3, 2) which would represent the 3rd 'heading' and
        2nd 'chapter' item. Some of the orders may be reset, but the first item
        should not--e.g. the 'heading' count should represent the running count
        of all headings, while the chapter count may be reset. This ensures that
        the order of labels is preserved when the counter of sub-kinds are
        reset.
        (see :class:`OrderLabels
        <disseminate.label_manager.processors.OrderLabels>`)
    """

    doc_id = None
    id = None
    kind = None
    order = None

    def __init__(self, doc_id, id, kind, mtime=None, order=None):
        self.doc_id = doc_id
        self.id = id
        self.mtime = mtime
        self.order = order

        # Wrap the kind in a tuple, if it's a string
        self.kind = (kind,) if isinstance(kind, str) else kind

    def __repr__(self):
        cls_name = self.__class__.__name__
        if all(isinstance(i, tuple) or isinstance(i, list)
               for i in (self.kind, self.order)):
            kind_str = ", kind: "
            kind_str += ", ".join(['{}[{}]'.format(k, o)
                                   for k, o in zip(self.kind, self.order)])
        else:
            kind_str = ''
        return "{}(doc_id: '{}', id: '{}'{})".format(cls_name, self.doc_id,
                                                     self.id, kind_str)

    @property
    def number(self):
        """The number for the label's most specific kind."""
        if isinstance(self.order, tuple) and len(self.order) > 0:
            return self.order[-1]
        else:
            return None

    @property
    def mtime(self):
        return getattr(self, '_mtime', None)

    @mtime.setter
    def mtime(self, value):
        """An mtime setter to make sure the modification time only increases"""
        current_value = getattr(self, '_mtime', None)
        if (not isinstance(current_value, float) or
           (isinstance(value, float) and value > current_value)):
            setattr(self, '_mtime', value)
