"""
Terminal utilities in the CLI.
"""
import shutil

try:
    from termcolor import colored
except ModuleNotFoundError:
    def colored(s, *args, **kwargs):
        return s


def term_width():
    """Retrieve the current width of the terminal."""
    return shutil.get_terminal_size((80, 20))[0]  # 80-column default


def fill_string(start, end, start_len=None, end_len=None, spacer=' ',
                width=None):
    """Prints a start string and end string to fill a line on the terminal
    using the spacer character."""
    start_len = len(start) if start_len is None else start_len
    end_len = len(end) if end_len is None else end_len
    width = width if width is not None else term_width()
    return (start +
            spacer * (width - start_len - end_len) +
            end)
