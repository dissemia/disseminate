"""
A base class for label processors.
"""
from textwrap import TextWrapper

from ...utils.classes import all_subclasses, weakattr


class ProcessLabels(object):
    """A base class for label processor functions.

    New processors are created by subclassing this class, setting and order
    and overriding the ``__call__`` method.

    Parameters
    ----------
    context : :obj:`DocumentContext
        <disseminate.documents.document_context.DocumentContext>`
        The context for the document that owns the label manager.

    Attributes
    ----------
    order : int
        The order (in ascending order) of the processor in the processing chain
        for tags.
    short_desc : str
        The short description for the procedure conducted by this label
        processor
    includes : Set[:class:`Label <disseminate.label_manager.types.Label>`]
        If specified, the labels with this type or types (or a subclass of this
        type) will be included by the filter method.
    excludes : Set[:class:`Label <disseminate.label_manager.types.Label>`]
        If specified, the labels with this type or types (or a subclass of
        this type) will be excluded by the filter method.
    """

    _instances = None
    context = weakattr
    order = 1000
    short_desc = None

    includes = None
    excludes = None

    def __init__(self, context):
        self.context = context

    def __call__(self, registered_labels, collected_labels, *args, **kwargs):
        """The tag processing function to override."""
        pass

    @classmethod
    def processors(self, context):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        # Instantiate subclasses, if it hasn't been done so already
        subclasses = all_subclasses(ProcessLabels)
        return sorted([subcls(context=context) for subcls in subclasses],
                      key=lambda x: getattr(x, 'order'))

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
