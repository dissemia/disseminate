"""
A base class for processing tags.
"""
from ..tag import Tag


class ProcessTag(object):
    """A processor function object for tags.

    Parameters
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    """

    _instances = []
    order = 1

    def __init__(self, order):
        self.order = order

        # Add the instance to the class's list of instances, sorted by order
        instances = sorted(ProcessTag._instances + [self],
                           key=lambda x: getattr(x, 'order'))
        ProcessTag._instances.clear()
        ProcessTag._instances += instances

    def __call__(self, tag):
        """The tag processing function to override."""
        pass

    @classmethod
    def processors(cls):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        return cls._instances


Tag.ProcessTag = ProcessTag
