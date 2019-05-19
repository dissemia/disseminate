"""
Command-line interface tools for Checkers
"""
from .term import fill_string, colored
from ..checkers import Checker


def ok(check_passed):
    """Format a bool, like True or False, to a pass/fail string."""
    s = '['
    if check_passed:
        s += colored("PASS", color='green', attrs=['bold'])
    else:
        s += colored("FAIL", color='red', attrs=['bold'])
    s += ']'
    return s, 6


def print_checkers():
    """Print the availabilitiy of executables and packages from the checkers.
    """
    # Get the checker subclasses
    checker_subclses = Checker.checker_subclasses()

    # Got through each checker
    for checker_subcls in checker_subclses:
        checker = checker_subcls()

        # Do an overall check
        checker.check_required(raise_error=False)

        pass_check = checker.check_required()
        ok_str, ok_len = ok(pass_check)
        target_str = fill_string("Test for {} targets".format(checker.target),
                                 end=ok_str, end_len=ok_len)

        print(target_str)
