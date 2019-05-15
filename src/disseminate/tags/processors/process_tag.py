"""
A base class for tag processors.
"""
from abc import abstractmethod

from ...processors import ProcessorABC
from ..factory import TagFactory


class ProcessTag(ProcessorABC):
    """A base class for tag processor functions.

    New processors are created by subclassing this class, setting and order
    and overriding the ``__call__`` method.

    Parameters
    ----------
    tag_base_cls : :class:`Tag <disseminate.tags.tag.Tag>`
        The base class for Tag objects.
    tag_factory : Optional[:obj:`TagFactory \
        <disseminate.tags.tag_factory.TagFactory>`]
        The tag factory object to create new tags.
    """

    tag_base_cls = None
    tag_factory = None

    #: Reuse instances created by the processors method.
    #: The tag_base_cls and tag_factory should be universal when running
    #: disseminate; they're not specific to an individual document.
    store_instances = True

    def __init__(self, tag_base_cls, tag_factory=None):
        self.tag_base_cls = tag_base_cls
        self.tag_factory = (TagFactory(tag_base_cls=tag_base_cls)
                            if tag_factory is None else tag_factory)

    @abstractmethod
    def __call__(self, tag):
        pass
