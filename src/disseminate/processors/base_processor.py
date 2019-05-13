"""
The base processor offers an abstract base class for processor classes.
"""
from abc import ABC, ABCMeta, abstractmethod
import re

from ..utils.classes import all_subclasses


_re_clean_spacing = re.compile(r'\s{2,}|\n')


class MetaProcessorABC(ABCMeta):
    """Metaclass to initialize ProcessorABC classes."""

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
    labels and other objects."""

    short_desc = None
    module = None
    order = 0

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @classmethod
    def processor_clses(cls):
        """A sorted list of the processor classes."""
        return sorted(all_subclasses(cls), key=lambda x:getattr(x, 'order'))

    @classmethod
    def processors(cls, *args, **kwargs):
        """A sorted list (by order, in ascending order) of processor
        instances."""
        # Instantiate subclasses, if it hasn't been done so already
        return [subcls(*args, **kwargs) for subcls in cls.processor_clses()]



