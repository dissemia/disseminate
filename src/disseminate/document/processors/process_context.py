"""
A base class for context processors.
"""
from abc import abstractmethod

from ...processors import ProcessorABC


class ProcessContext(ProcessorABC):
    """A base class for context processor functions.

    New processors are created by subclassing the ProcessContext class, setting
    and order and overriding the ``__call__`` method.
    """

    #: Reuse processor instances created by the processors method
    store_instances = True

    @abstractmethod
    def __call__(self, context):
        pass
