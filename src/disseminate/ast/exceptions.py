"""
Exceptions for Abstract Syntax Trees (ASTs)
"""


class AstException(Exception):
    """An error was encountered while processing the Abstract Syntax Tree"""
    pass


class ParseError(Exception):
    """An error was encountered when parsing a document source file."""
    pass
