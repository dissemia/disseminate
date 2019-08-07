"""
Exceptions for check classes.
"""


class Checker(Exception):
    pass


class MissingHandler(Checker):
    """A handler for a specified category is not available to the checker."""
    pass
