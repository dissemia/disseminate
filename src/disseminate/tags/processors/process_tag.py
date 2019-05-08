"""
A base class for tag processors.
"""
from textwrap import TextWrapper

from ..tag import Tag
from ...utils.classes import all_subclasses


class ProcessTag(object):
    """A base class for tag processor functions.

    New processors are created by subclassing this class, setting and order
    and overriding the ``__call__`` method.

    Parameters
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    """

    _instances = None
    order = 1000
    short_desc = None

    def __call__(self, tag):
        """The tag processing function to override."""
        pass

    @classmethod
    def processors(cls):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        if cls._instances is None:
            # Instantiate subclasses, if it hasn't been done so already
            subclasses = all_subclasses(ProcessTag)
            cls._instances = sorted([subcls() for subcls in subclasses],
                                    key=lambda x: getattr(x, 'order'))
        return cls._instances

    def print_msg(self):
        """Returns a string for printing the details on the tag processor
        to the terminal"""
        wrapper = TextWrapper(initial_indent=' ' * 4,
                              subsequent_indent=' ' * 6)

        # Get the class name
        msg = self.__class__.__name__ + "\n"

        # Get the short description, if available
        if self.short_desc:
            msg += wrapper.fill(self.short_desc) + '\n'

        # Print the module of the processor
        mod_str = "module: {}".format(self.__class__.__module__)
        msg += wrapper.fill(mod_str) + '\n'

        # print the order of the processor
        ord_str = "order: {}".format(self.order)
        msg += wrapper.fill(ord_str) + '\n'
        return msg


Tag.processtag_cls = ProcessTag
