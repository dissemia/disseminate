from .label import Label


class DocumentLabel(Label):
    """A label for documents.
    """
    title = None

    def __init__(self, doc_id, id, kind, title, order=None):
        super().__init__(doc_id=doc_id, id=id, kind=kind, order=order)
        self.title = title
