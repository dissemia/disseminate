"""
Utilities for testing.
"""


def strip_leading_space(string, no_spaces=4):
    """Strip leading spaces at the start of newlines in a string.
    """
    pieces = [s[no_spaces:] if s.startswith(" " * no_spaces) else s
              for s in string.split('\n')]
    return '\n'.join(pieces)
