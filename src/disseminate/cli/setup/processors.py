"""
Command-line interface tools for Processors
"""
from textwrap import TextWrapper

from click import style

from ..term import term_width


def print_processors(processor_base_cls):
    """Given an processor base class (derived from
    :class:`disseminate.processors.ProcessorABC`), print the processors
    available.

    Parameters
    ----------
    processor_base_cls : :class:`.ProcessorABC`
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
        msg += style(cls_name, bold=True, underline=True)
        msg += '\n'

        # Get the short description, if available
        if getattr(processor_cls, 'short_desc', None) is not None:
            msg += wrap_desc.fill(processor_cls.short_desc) + '\n'

        # Get the module, if available
        if getattr(processor_cls, 'module', None) is not None:
            mod_str = style("module:", fg='cyan', bold=True)
            mod_str += " {}".format(processor_cls.module)
            msg += wrap_fields.fill(mod_str) + '\n'

        # Get the module, if available
        if getattr(processor_cls, 'order', None) is not None:
            order_str = style("order:", fg='cyan', bold=True)
            order_str += " {}".format(processor_cls.order)
            msg += wrap_fields.fill(order_str) + '\n'

        print(msg)
