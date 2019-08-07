"""
A base class for label processors.
"""
from abc import abstractmethod

from ...processors import ProcessorABC
from ...utils.classes import weakattr


class ProcessLabels(ProcessorABC):
    """A base class for label processor functions.

    New processors are created by subclassing this class, setting and order
    and overriding the ``__call__`` method.

    Parameters
    ----------
    context : :obj:`DocumentContext <.DocumentContext>`
        The context for the document that owns the label manager.

    Attributes
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    short_desc : str
        The short description for the procedure conducted by this label
        processor
    includes : Set[:class:`Type[Label] <.types.Label>`]
        If specified, the labels with this type or types (or a subclass of this
        type) will be included by the filter method.
    excludes : Set[:class:`Type[Label] <.types.Label>`]
        If specified, the labels with this type or types (or a subclass of
        this type) will be excluded by the filter method.
    """

    _instances = None
    context = weakattr
    order = 1000

    includes = None
    excludes = None

    #: Do not store process instances; create new processors every time the
    #: :meth:`processors <.ProcessorABC.processors>` method is
    #: executed. This is because the processors store the context of documents,
    #: which are different for each document.
    store_instances = False

    def __init__(self, context):
        self.context = context

    def filter(self, labels):
        """Filter labels based on label types listed in the includes and
        excludes attribute."""
        if self.includes:
            labels = [label for label in labels if
                      any(isinstance(label, t) for t in self.includes)]
        if self.excludes:
            labels = [label for label in labels if not
                      any(isinstance(label, t) for t in self.excludes)]
        return labels

    @abstractmethod
    def __call__(self, registered_labels, collected_labels):
        pass
