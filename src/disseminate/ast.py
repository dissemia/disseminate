"""
Functions for processing abstract syntax trees (ASTs).
"""
import regex
from lxml.builder import E
from lxml import etree

from .tags import TagFactory, Tag
from .attributes import kwargs_attributes
from . import settings


class AstException(Exception): pass

class ParseError(Exception):
    """An error was encountered when parsing an AST."""
    pass

control_char = r'@'


re_tag = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
                       r'(?P<attributes>\[[^\]]+\])?'
                       r'{(?P<content>(?>[^{}@]+|(?R))*)})')


def process_ast(s, local_context=None, level=1):
    """Parses a string into an AST comprising a list of lists with strings and
    tags.

    Parameters
    ----------
    s : str
        The string to process.
    level : int, optional
        The current level of the ast.

    Returns
    -------
    ast : list of str or list
        The AST is a list of string or nested lists, which may themselves
        containt strings or nested lists.

    Raises
    ------
    AstException
        Raises an AstException if the max depth has been achieved
        (settings.ast_max_depth). This is an attempt to foil the Billion Laughs
        attack.
    """
    if level >= settings.ast_max_depth:
        msg = ("The maximum depth of '{}' has been reached in the AST. "
               "Additional levels can be set by the 'settings.ast_max_depth'.")
        raise AstException(msg.format(settings.ast_max_depth))
    if not isinstance(local_context, dict):
        local_context = dict()

    ast = []
    current_pos = 0
    factory = TagFactory()
    validator = ASTValidator()

    for m in re_tag.finditer(s):
        # Find the match's start and end positions in the string
        start, end = m.span()

        # Find the string up to this match and find the current line number
        string = s[current_pos:start]

        # Validate the string and match to make sure there are no errors.
        validator.validate(string, m)

        # Add the validated string to the ast
        ast.append(string)

        # Reset the current position to the end of this match
        current_pos = end

        # Parse the match's content
        d = m.groupdict()
        tag_name = m['tag']
        tag_content = process_ast(m['content'], local_context, level + 1)
        tag_attributes = m['attributes']
        ast.append(factory.tag(tag_name=tag_name,
                               tag_content=tag_content,
                               tag_attributes=tag_attributes,
                               local_context=local_context))

    # Add the end of the string, if it's valid
    string = s[current_pos:]
    validator.validate(string, None)
    ast.append(string)

    return ast


class ASTValidator:
    """A class to validate ASTs."""

    def __init__(self, line_no=1):
        self.line_no = line_no

    def validate(self, string, match=None):
        """Validate unmatched strings and regex matches."""
        # Get a list of all available validate_methods
        validate_methods = [getattr(self, i) for i in dir(self)
                            if i.startswith("validate_")]

        # Run the validations. If any return a string instead of True, raise
        # a ParseError exception
        for method in validate_methods:
            return_value = method(string, match)
            if isinstance(return_value, str):
                raise ParseError(return_value)

        # increment the line numbers from the unmatched string
        self.line_no += string.count("\n")

        # increment the line numbers from the regex match
        if match:
            matched_string = match.string[slice(*match.span())]
            self.line_no += matched_string.count("\n")

        return True

    _e_opentag = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
                              r'(?P<attributes>\[[^\]]+\])?'
                              r'{)')

    def validate_closed_tags(self, string, match=None):
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
        # Look for malformed tags (i.e. tags with open curly brackets)
        m = self._e_opentag.search(string)
        if m:
            # Get the problematic string
            match_positions = m.span()
            problem_string = string[slice(*match_positions)]

            # Find its line number
            self.line_no += problem_string.count("\n")

            # Raise an exception
            return "Tag not closed on line {}: {}".format(self.line_no,
                                                          problem_string)
        else:
            return True

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



def validate_closed_tags(string):
    """Validates that all tags are closed in a given string.

    Parameters
    -------
    string : str
        A string in an AST that should be validated

    Return
    ------
    bool or span
        If True is returned, then the string is validated
        If a span is returns (start, end), then the following range in
        the string is malformed.
    """
    # Look for malformed tags (i.e. tags with open braces)
    m = e_opentag.search(string)
    if m:
        return m.span()
    else:
        return True


def convert_html(ast, root_tag=settings.html_root_tag,
                 pretty_print=settings.html_pretty):
    """Converts an ast to html.

    Parameters
    ----------
    root_tag : str, optional
        The tag to use to wrap the html. (ex: 'body')
    pretty_print : bool, optional
        Add newlines and indentation to html tags.

    Returns
    -------
    html_str : str
        A processed html string.
    """

    if isinstance(ast, Tag):
        if isinstance(ast.content, list):
            return E(ast.name,
                     *[convert_html(i) for i in ast.content])
        else:
            # If the tag has an html method, use it to format the html.
            if getattr(ast, 'html', None) is not None:
                return ast.html()

            # Only include content i the content is not None or the empty
            # string
            content = (ast.content.strip()
                       if isinstance(ast.content, str)
                       else ast.content)
            content = [content, ] if content else []

            # Prepare the attributes
            kwargs = (kwargs_attributes(ast.attributes)
                      if ast.attributes
                      else dict())
            return E(ast.name,
                     *content,
                     **kwargs)

    elif isinstance(ast, list):
        # Add a new line to the end, if needed
        elements = [convert_html(i) for i in ast]
        if (not isinstance(elements[-1], str) or
            elements[-1] and elements[-1][-1] != '\n'):
            elements.append('\n')

        return etree.tostring(E(root_tag, *elements),
                              pretty_print=pretty_print).decode("utf-8")
    else:
        return ast


def print_ast(ast, level=1):
    """Pretty print an AST with one entry per line and indentation for nested
    levels.

    Parameters
    ----------
    ast : list of str or list
        The AST is a list of string or nested lists, which may themselves
        containt strings or nested lists.
    level : int, optional
        The current level of the ast.
    """
    assert isinstance(ast, list)

    print()
    for count, item in enumerate(ast, 1):
        if isinstance(item, str):
            print("{}.{}:".format(level, count),
                  "  " * level, repr(item))
            continue

        if (hasattr(item, 'content')
            and not isinstance(item.content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item)

        if (hasattr(item, 'content')
            and isinstance(item.content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item.name, "{")
            print_ast(item.content, level + 1)
            print("    " + "  " * level + "}")

