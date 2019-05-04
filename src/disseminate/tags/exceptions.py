"""Exceptions for Tag objects"""


class TagError(Exception):
    """An error was encountered while interpreting a tag."""
    pass


def assert_content_str(content):
    """Assert that the tag contents are a string, and raise an exception if
    it isn't.

    Raises
    ------
    TagError
        If the content isn't a string, raise a TagError.
    """
    if not isinstance(content, str):
        msg = ("The tag contents must be a string. "
               "The followed content was inserted: {}")
        raise TagError(msg.format(content))
