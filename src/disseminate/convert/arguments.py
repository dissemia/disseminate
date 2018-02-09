"""
Arguments for converters
"""
import os.path
import logging


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

    def __init__(self, name, value_string, required=True):
        self.name = name
        self.value_string = value_string
        self.default = None
        self.required = required

        if not self.is_valid():
            msg = ("The parameter '{}' did not have a valid value. "
                   "'{}' was given".format(name, value_string))
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
        return self.value_string.isnumeric()


class PositiveFloatArgument(Argument):
    """A positive floating point number."""

    def is_valid(self):
        try:
            value = float(self.value_string)
        except ValueError:
            return False
        return value > 0.0


class PathArgument(Argument):
    """A path argument.

    The directory must exist for this path to be considered valid.
    """

    def is_valid(self):
        split = os.path.split(self.value_string)
        return os.path.isdir(split[0]) or os.path.isdir(self.value_string)
