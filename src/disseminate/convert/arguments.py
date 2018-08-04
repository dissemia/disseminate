"""
Arguments for converters
"""
import logging
from ..paths import SourcePath, TargetPath


class ArgumentError(Exception):
    """An error was encountered in a required argument."""
    pass


class Argument(object):
    """A command argument.

    Parameters
    ----------
    name : str
        The name of the argument
    value_string : str
        The value (string) of the argument
    default : str or None, optional
        A default value of the argument, if available.
    """

    required = False

    def __init__(self, name, value, required=True):
        self.name = name
        self.value = value
        self.default = None
        self.required = required

        if not self.is_valid():
            msg = ("The parameter '{}' did not have a valid value. "
                   "'{}' was given".format(name, value))
            if required:
                raise ArgumentError(msg)
            else:
                logging.warning(msg)

    def is_valid(self):
        """Evaluate whether the given 'value_string' for the argument with
        'name' is a valid value for this argument."""
        return False


class PositiveIntArgument(Argument):
    """A positive integer argument"""

    def is_valid(self):
        return self.value.isnumeric()


class PositiveFloatArgument(Argument):
    """A positive floating point number."""

    def is_valid(self):
        try:
            value = float(self.value)
        except ValueError:
            return False
        return value > 0.0


class SourcePathArgument(Argument):
    """A path argument.

    The directory must exist for this path to be considered valid.
    """

    def is_valid(self):
        return (isinstance(self.value, SourcePath) and
                (self.value.is_dir() or self.value.parent.is_dir()))


class TargetPathArgument(Argument):
    """A path argument.

    The directory must exist for this path to be considered valid.
    """

    def is_valid(self):
        return (isinstance(self.value, TargetPath) and
                (self.value.is_dir() or self.value.parent.is_dir()))
