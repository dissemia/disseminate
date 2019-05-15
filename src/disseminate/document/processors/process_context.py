"""
A base class for context processors.
"""
from ...processors import ProcessorABC


class ProcessContext(ProcessorABC):
    """A base class for context processor functions.

    New processors are created by subclassing the ProcessContext class, setting
    and order and overriding the ``__call__`` method.

    Parameters
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    """
    pass
