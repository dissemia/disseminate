"""
The label base class for the label manager.
"""


class Label(object):
    """A label used for referencing.

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
    order : Optional[Tuple[int]]
        The order/number of the label. The order is a tuple of integers with a
        length that matches the 'kind' tuple. Each entry represents the
        order/number of each kind  ex: for a kind ('heading', 'chapter') could
        have an order of (3, 2) which would represent the 3rd 'heading' and
        2nd 'chapter' item. Some of the orders may be reset, but the first item
        should not--e.g. the 'heading' count should represent the running count
        of all headings, while the chapter count may be reset. This ensures
        that the order of labels is preserved when the counter of sub-kinds are
        reset.
        (see :class:`OrderLabels
        <disseminate.label_manager.processors.OrderLabels>`)
    """

    doc_id = None
    id = None
    kind = None
    order = None

    def __init__(self, doc_id, id, kind, order=None):
        self.doc_id = doc_id
        self.id = id
        self.order = order

        # Wrap the kind in a tuple, if it's a string
        self.kind = (kind,) if isinstance(kind, str) else kind

    def __repr__(self, **params):
        cls_name = self.__class__.__name__
        if all(isinstance(i, tuple) or isinstance(i, list)
               for i in (self.kind, self.order)):
            kind_str = ", kind: "
            kind_str += ", ".join(['{}[{}]'.format(k, o)
                                   for k, o in zip(self.kind, self.order)])
        else:
            kind_str = ''
        msg = "{}(doc_id: '{}', id: '{}'{}".format(cls_name, self.doc_id,
                                                   self.id, kind_str)
        if params:
            attr_str = ", ".join(
                "{}: '{}'".format(k, v) for k, v in sorted(params.items()))
            msg += " " + attr_str + ")"
        else:
            msg += ")"
        return msg

    def __lt__(self, other):
        return (self.doc_id, self.id) < (other.doc_id, other.id)

    def __le__(self, other):
        return (self.doc_id, self.id) <= (other.doc_id, other.id)

    def __gt__(self, other):
        return (self.doc_id, self.id) > (other.doc_id, other.id)

    def __ge__(self, other):
        return (self.doc_id, self.id) >= (other.doc_id, other.id)

    def __eq__(self, other):
        return (self.doc_id, self.id) == (other.doc_id, other.id)

    def __ne__(self, other):
        return (self.doc_id, self.id) != (other.doc_id, other.id)

    def __hash__(self):
        return hash((self.__class__.__name__, self.doc_id, self.id))

    @property
    def number(self):
        """The number for the label's most specific kind."""
        if isinstance(self.order, tuple) and len(self.order) > 0:
            return self.order[-1]
        else:
            return None
