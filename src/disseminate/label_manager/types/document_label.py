from .label import Label


class DocumentLabel(Label):
    """A label for documents.
    """
    title = None

    def __init__(self, doc_id, id, kind, mtime, title,
                 order=None):
        super().__init__(doc_id=doc_id, id=id, kind=kind, mtime=mtime,
                         order=order)
        self.title = title
