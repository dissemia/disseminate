"""
Exceptions for documents
"""


class DocumentException(Exception):
    """An error was encountered in creating, setting up or rendering a
    document."""
    pass


class MissingTargetException(DocumentException):
    """A target was request that is not available for the document."""
    pass
