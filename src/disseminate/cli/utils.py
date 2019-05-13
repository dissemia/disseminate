"""
Utilities for rendering the command-line interface.
"""
from textwrap import TextWrapper
import shutil

try:
    from termcolor import colored
except ModuleNotFoundError:
    colored = None

from .. import settings


def term_width():
    """Retrieve the current width of the terminal."""
    return shutil.get_terminal_size((80, 20))[0]  # 80-column default


def print_processors(processor_base_cls):
    """Given an processor base class (derived from
    :class:`disseminate.processors.ProcessorABC`), print the processors
    available.

    Parameters
    ----------
    processor_base_cls : :class:`disseminate.processors.ProcessorABC`
        A *concrete* implementation class of the ProcessorABC.
    *args, **kwargs
        The arguments and keyword arguments passed to initiate the
        processor_base_cls class.

    Returns
    -------
    None
    """

    wrap_desc = TextWrapper(initial_indent=' ' * 4,
                            subsequent_indent=' ' * 4,
                            width=term_width())
    wrap_fields = TextWrapper(initial_indent=' ' * 4,
                              subsequent_indent=' ' * 6,
                              width=term_width())

    processor_clses = processor_base_cls.processor_clses()
    for count, processor_cls in enumerate(processor_clses, 1):
        # Get the class name
        cls_name = processor_cls.__name__
        msg = "{count}. ".format(count=count)
        msg += (colored(cls_name, attrs=['bold', 'underline'])
                if settings.colored_term and colored is not None else
                cls_name)
        msg += '\n'

        # Get the short description, if available
        if getattr(processor_cls, 'short_desc', None) is not None:
            msg += wrap_desc.fill(processor_cls.short_desc) + '\n'

        # Get the module, if available
        if getattr(processor_cls, 'module', None) is not None:
            mod_str = (colored("module:", color='cyan', attrs=['bold'])
                       if settings.colored_term and colored is not None else
                       "module:")
            mod_str += " {}".format(processor_cls.module)
            msg += wrap_fields.fill(mod_str) + '\n'

        # Get the module, if available
        if getattr(processor_cls, 'order', None) is not None:
            order_str = (colored("order:", color='cyan', attrs=['bold'])
                         if settings.colored_term and colored is not None else
                         "order:")
            order_str += " {}".format(processor_cls.order)
            msg += wrap_fields.fill(order_str) + '\n'

        print(msg)
