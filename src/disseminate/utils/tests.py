"""
Utilities for testing.
"""


def strip_leading_space(string, no_spaces=4):
    """Strip leading spaces at the start of newlines in a string.
    """
    pieces = [s[no_spaces:] if s.startswith(" " * no_spaces) else s
              for s in string.split('\n')]
    return '\n'.join(pieces)


def cleanup_subclass(subcls):
    """Delete and clean-up test subclasses so that the subclass no longer
    shows up in the parent class's __subclasses__() method.
    """
    # Create a mock other parent class
    class OtherClass(object):
        pass

    # Reassign the subclasses's base
    subcls.__bases__ = (OtherClass,)

    # Delete the subclass
    del subcls
