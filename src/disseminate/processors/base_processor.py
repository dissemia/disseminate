"""
The base processor offers an abstract base class for processor classes.
"""
from abc import ABC, ABCMeta, abstractmethod
import re

from ..utils.classes import all_subclasses


_re_clean_spacing = re.compile(r'\s{2,}|\n')


class MetaProcessorABC(ABCMeta):
    """Metaclass to initialize ProcessorABC classes.

    This metaclass initializes the ``short_desc`` and ``module`` attributes of
    the class.
    """

    def __init__(cls, name, bases, attrs):

        # Set the short description by using the first line of the class
        # docstring, if available
        docstring = getattr(cls, '__doc__', None)
        docstring = (docstring.split('\n\n')[0]
                      if isinstance(docstring, str) else '')
        cls.short_desc = _re_clean_spacing.sub(' ', docstring)

        # Set the module for the processor
        cls.module = cls.__module__

        super().__init__(name, bases, attrs)


class ProcessorABC(ABC, metaclass=MetaProcessorABC):
    """A processor abstract base class for processors of contexts, tags,
    labels and other objects.

    Attributes
    ----------
    short_desc : str
        The short description of the processor, constructed from the first line
        of the process class docstring, if available.
    module : str
        The path for the module that defines the processor.
    order : int
        The order of the processor. This is used to order processors when
        many processor sub-classes are executed in sequence. A lower order
        represents an earlier processor.
    store_instances : bool
        If True, processor instances returned by the :meth:`processors` class
        method will be cached to save memory.
    """

    short_desc = None
    module = None
    order = 0

    store_instances = False
    _instances = None

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @classmethod
    def processor_clses(cls):
        """A sorted list of the processor classes."""
        return sorted(all_subclasses(cls), key=lambda x: getattr(x, 'order'))

    @classmethod
    def processors(cls, *args, **kwargs):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        if cls._instances is not None:
            return cls._instances

        # Instantiate subclasses, if it hasn't been done so already
        instances = [subcls(*args, **kwargs)
                     for subcls in cls.processor_clses()]

        if cls.store_instances:
            cls._instances = instances

        return instances




