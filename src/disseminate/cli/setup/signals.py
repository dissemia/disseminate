"""
Command-line interface tools for Signals
"""
from textwrap import TextWrapper
from string import ascii_lowercase

from click import style

from ..term import term_width
from ...utils.string import stub


def print_signals(signal_namespace):
    """Given an signal namespace, print all signals and connected receivers.

    Parameters
    ----------
    signal_namespace : :obj:`.signals.signals.Namespace`
        The namespace for all signals.

    Returns
    -------
    None
    """

    wrap_desc = TextWrapper(initial_indent=' ' * 4,
                            subsequent_indent=' ' * 4,
                            width=term_width())
    wrap_fields = TextWrapper(initial_indent=' ' * 4,
                              subsequent_indent=' ' * 7,
                              width=term_width())
    lowercase = list(ascii_lowercase)

    for count, (name, signal) in enumerate(signal_namespace.items(), 1):
        msg = "{count}. ".format(count=count)
        msg += style(name, bold=True, underline=True)
        msg += '\n'

        # Get the docstring (first line), if available
        if getattr(signal, '__doc__', None) is not None:
            docstring = stub(signal.__doc__)
            msg += wrap_desc.fill(docstring) + '\n'

        # Get the receivers for the signal
        receivers = list(enumerate(sorted(signal.receivers_dict().items())))

        if len(receivers) > 0:
            rec_str = style("Receivers:", bold=True)
            msg += "\n" + wrap_desc.fill(rec_str) + "\n"

        for count, (order, receiver) in receivers:
            rec_str = (lowercase[count] if count < len(lowercase) else
                       str(count))
            rec_str += ". "
            rec_str += style("{}".format(receiver.__name__), fg='cyan')

            if receiver.__doc__ is not None:
                docstring = stub(receiver.__doc__)
                rec_str += " - " + docstring
            msg += wrap_fields.fill(rec_str) + "\n"

            rec_str = "   order: " + str(order)
            msg += wrap_fields.fill(rec_str) + '\n'

        print(msg)
