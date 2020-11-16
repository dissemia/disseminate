"""
Exceptions for documents
"""


class DocumentException(Exception):
    """An error was encountered in creating, setting up or rendering a
    document."""
    pass


class TargetNotFound(DocumentException):
    """An error raised if a document target was requested but not found."""
    pass
