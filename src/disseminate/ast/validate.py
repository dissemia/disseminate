"""
Functions and classes to validate the AST as it's being processed.
"""
import regex
from ..tags import Tag
from .utils import count_ast_lines


class ParseError(Exception):
    """An error was encountered when parsing a document source file."""
    pass


class ValidateAndCleanAST:
    """A class to validate and clean ASTs.

    Parameters
    ----------
    name : str, optional
        The name of the AST. This is typically the src_filepath of the markup
        source file that was used to generate the AST.
    line_offset : int, optional
        If specified, line numbers will be offset by this number. A line_offset
        can occur when a header is stripped from a markup source file.
    """

    def __init__(self, name=None, line_offset=None):
        self.name = name
        self.line_offset = line_offset

    def validate(self, ast):
        """Validate unmatched strings and regex matches."""

        # First format the ast
        ast = self.join_strings(ast)
        self.count_tags(ast)

        validate_methods = [getattr(self, i) for i in dir(self)
                            if i.startswith("validate_")]

        # Run the validations. If any return a string instead of True, raise
        # a ParseError exception
        for method in validate_methods:
            return_value = method(ast)
            if isinstance(return_value, str):
                raise ParseError(return_value)

        return ast

    _opentag = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
                               r'(?P<attributes>\[[^\]]+\])?'
                               r'{)')

    def validate_closed_tags(self, ast):
        """Validates that all tags are closed in a given string.

        Parameters
        ----------
        string : str
            A string in an AST that should be validated

        Return
        ------
        bool or str
            If True is returned, then the string is validated
            If a msg is returned, then the validation didn't pass. The msg
            is an error message.
        """
        # Keep track of the previously analyzed ast elements for line number
        # counting and error reporting
        previous_ast = []

        for i in ast:
            # see if there's a match for an opentag
            match = self._opentag.search(i) if isinstance(i, str) else None

            # If a match was found, return the error/exception message
            if match:
                # Determine the line number up to the match
                substring = i[:match.end()]
                line_number = count_ast_lines(previous_ast)
                line_number += substring.count('\n')

                msg = ("{}: ".format(self.name) if isinstance(self.name, str)
                       else '')

                msg += "Tag not closed on line {}: {}".format(line_number, i)
                return msg

            previous_ast.append(i)

        return True

    def join_strings(self, ast):
        """Join consecutive strings in an ast and split at new lines

        Parameters
        ----------
        ast : list or tag (:obj:`disseminate.Tag`
            The abstract syntax tree to process.

        Returns
        -------
        ast : list or tag (:obj:`disseminate.Tag`
            The processed abstract syntax tree.
        """
        # Get the ast lists to iterate over. This function only works on lists:
        # the ast either a list itself or it's a tag with a list for its
        # contents otherwise, just return the ast
        if isinstance(ast, list):
            source_ast = ast
            new_ast = []
        elif isinstance(ast, Tag) and isinstance(ast.content, list):
            source_ast = ast.content
            ast.content = []
            new_ast = ast.content
        else:
            return ast

        for i in source_ast:
            if isinstance(i, Tag):
                new_ast.append(self.join_strings(i))

            elif isinstance(i, list):
                new_ast.append(self.join_strings(i))

            elif isinstance(i, str):
                # strings either need to be added to the last element, if that
                # is a string also, or it is simply added to the ast.
                if len(new_ast) > 0 and isinstance(new_ast[-1], str):
                    new_ast[-1] += i
                else:
                    new_ast.append(i)

            else:
                new_ast.append(i)

        return ast if isinstance(ast, Tag) else new_ast

    def count_tags(self, ast, line_number=None):
        """Add a line_number attribute to tags to identify the starting line
        number of a tag.

        Parameters
        ----------
        ast : list or tag (:obj:`disseminate.Tag`
            The abstract syntax tree to process.
        line_number : int, optional
            The initial line number to use in the count.

        Returns
        -------
        total_line_number : int
            The total number of lines.
        """
        # For the root ast, get the line_number
        if line_number is None:
            line_number = (self.line_offset
                           if isinstance(self.line_offset, int) else 1)

        # Process the input ast
        if isinstance(ast, Tag):
            # Deal with tags directly. Either process their content if it's a
            # list or label the tag's line_number. In either case, the tag's
            # line number should be set
            ast.line_number = line_number

            if isinstance(ast.content, list):
                ast = ast.content
            else:
                line_number += ast.content.count('\n')
                return line_number

        # Process ast lists
        for i in ast:
            if isinstance(i, str):
                # Process strings by counting newlines. Only strings can
                # advance the counter
                line_number += i.count('\n')
            elif isinstance(i, Tag):
                line_number = self.count_tags(i, line_number=line_number)
            elif isinstance(i, list):
                line_number = self.count_tags(i, line_number=line_number)

        return line_number
