"""
Functions and classes to validate the AST as it's being processed.
"""
import regex


class ParseError(Exception):
    """An error was encountered when parsing a document source file."""
    pass

class ASTValidator:
    """A class to validate ASTs as they're being processed."""

    def __init__(self, src_filepath):
        self.src_filepath = src_filepath

    def validate(self, ast):
        """Validate unmatched strings and regex matches."""

        validate_methods = [getattr(self, i) for i in dir(self)
                            if i.startswith("validate_")]

        # Run the validations. If any return a string instead of True, raise
        # a ParseError exception
        for method in validate_methods:
            return_value = method(ast)
            if isinstance(return_value, str):
                raise ParseError(return_value)

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
        for i in ast:
            print("{}: {}".format(type(i), i))
            if isinstance(i, str) and self._opentag.search(i):
                line_no = getattr(i, 'line_no', None)
                if line_no:
                    msg = "Tag not closed on line {}: {}".format(line_no, i)
                else:
                    msg = "Tag not closed: {}".format(i)

                return msg

        return True

        # Look for malformed tags (i.e. tags with open curly brackets)
    #     m = self._e_opentag.search(string)
    #     if m:
    #         # Get the problematic string
    #         match_positions = m.span()
    #         problem_string = string[slice(*match_positions)]
    #
    #         # Find its line number
    #         self.line_no += problem_string.count("\n")
    #
    #         # Return the error message
    #         if isinstance(self.src_filepath, str):
    #             msg = "({}) Tag not closed on line {}: {}"
    #             msg = msg.format(self.src_filepath, self.line_no,
    #                              problem_string)
    #         else:
    #             msg = "Tag not closed on line {}: {}"
    #             msg = msg.format(self.line_no, problem_string)
    #
    #         return msg
    #     else:
    #         return True

    # e_openattr = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
    #                            r'(?P<attributes>\[[^\]]+\]))')
    #
    # def valid_closed_attributes(self, string, match=None):
    #     """Validates that all tag attributes are closed in the given string.
    #
    #     Parameters
    #     ----------
    #     string : str
    #         A string in an AST that should be validated
    #
    #     Return
    #     ------
    #     bool or str
    #         If True is returned, then the string is validated
    #         If a msg is returned, then the validation didn't pass. The msg
    #         is an error message.
    #     """