"""
A base class for context processors.
"""

from ..utils.classes import all_subclasses


class ProcessContext(object):
    """A base class for context processor functions.

    New processors are created by subclassing the ProcessContext class, setting
    and order and overriding the ``__call__`` method.

    Parameters
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    """

    _instances = None
    order = 1000

    def __call__(self, context):
        """The context processing function to override."""
        pass

    @classmethod
    def processors(cls):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        if cls._instances is None:
            # Instantiate subclasses, if it hasn't been done so already
            subclasses = all_subclasses(ProcessContext)
            cls._instances = sorted([subcls() for subcls in subclasses],
                                    key=lambda x: getattr(x, 'order'))
        return cls._instances
