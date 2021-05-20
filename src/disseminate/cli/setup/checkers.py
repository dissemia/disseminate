"""
Command-line interface tools for Checkers
"""
from click import style

from ..term import fill_string
from ...checkers import Checker, All, Any, Optional

spaces_per_level = 2
width = 80


def print_single_check(msg, status, color=None, bold=False, spacer=' ',
                       level=1):
    """Print a single check line."""
    msg = (' ' * spaces_per_level * level) + msg  # indent
    status_str = '[{:^8}]  '.format(status)
    status_len = len(status_str)

    if color is not None:
        status_str = style(status_str, fg=color, bold=bold)
    return fill_string(msg, end=status_str, end_len=status_len, spacer=spacer,
                       width=width)


def print_dependencies(item, required=True, level=1):
    # Setup the status string
    available = getattr(item, 'available', None)
    if available is True:
        status_str, color, bold, spacer = 'PASS', 'green', True, ' '
    elif available is False and required:
        status_str, color, bold, spacer = 'FAIL', 'red', True, '.'
    elif available is False and not required:
        status_str, color, bold, spacer = 'MISSING', 'yellow', True, ' '
    else:
        status_str, color, bold, spacer = 'UNKNOWN', 'white', False, ' '

    if isinstance(item, All):
        # All are required
        msg = "Checking required dependencies for '{}'".format(item.category)
        msg = print_single_check(msg=msg, status=status_str, color=color,
                                 bold=bold, level=level, spacer=spacer)
        print(msg)
        for i in item:
            print_dependencies(item=i, required=True, level=level + 1)
    elif isinstance(item, Any):
        # One is required are required
        msg = ("Checking alternative dependencies for "
               "'{}'".format(item.category))
        msg = print_single_check(msg=msg, status=status_str, color=color,
                                 bold=bold, level=level, spacer=spacer)
        print(msg)
        for i in item:
            print_dependencies(item=i, required=False, level=level + 1)
    elif isinstance(item, Optional):
        # Optional
        # One is required are required
        msg = ("Checking alternative dependencies for "
               "'{}'".format(item.category))
        msg = print_single_check(msg=msg, status=status_str, color=color,
                                 bold=bold, level=level, spacer=spacer)
        print(msg)
        for i in item:
            print_dependencies(item=i, required=False, level=level + 1)
    elif hasattr(item, 'name'):
        msg = "Checking dependency '{}'".format(item.name)
        msg = print_single_check(msg=msg, status=status_str, color=color,
                                 bold=bold, level=level, spacer=spacer)
        print(msg)


def print_checkers():
    """Print the availabilitiy of executables and packages from the checkers.
    """
    # Get the checker subclasses
    checker_subclses = Checker.checker_subclasses()

    # Iterate through the checkers
    for checker_subcls in checker_subclses:
        checker = checker_subcls()

        # Do an overall check
        checker.check()

        # Print the checker status
        print_dependencies(checker)
