"""
Functions for processing abstract syntax trees (ASTs).
"""
import regex

from .tags import TagFactory
from . import settings


class AstException(Exception): pass


re_tag = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
                       r'(?P<attributes>\[[^\]]+\])?'
                       r'{(?P<content>(?>[^{}@]+|(?R))*)})')

def process_ast(s, level=1):
    """Parses a string into an AST comprising a list of lists with strings and
    tags.

    Parameters
    ----------
    s: str
        The string to process.
    level: int, optional
        The current level of the ast.

    Returns
    -------
    ast: list of str or list
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

    ast = []
    current_pos = 0
    factory = TagFactory()

    for m in re_tag.finditer(s):
        # Find the match's start and end positions in the string
        start, end = m.span()

        # Add string up to this match
        ast.append(s[current_pos:start])

        # Reset the current position to the end of this match
        current_pos = end

        # Parse the match's content
        d = m.groupdict()
        tag_type = m['tag']
        tag_content = process_ast(m['content'], level + 1)
        tag_attributes = m['attributes']
        ast.append(factory.tag(tag_type, tag_content, tag_attributes))

    # Add the end of the string
    ast.append(s[current_pos:])

    return ast


def print_ast(ast, level=1):
    """Pretty print an AST with one entry per line and indentation for nested
    levels."""
    assert isinstance(ast, list)

    print()
    for count, item in enumerate(ast, 1):
        if isinstance(item, str):
            print("{}.{}:".format(level, count),
                  "  " * level, repr(item))
            continue

        if (hasattr(item, 'tag_content')
            and not isinstance(item.tag_content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item)

        if (hasattr(item, 'tag_content')
            and isinstance(item.tag_content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item.tag_type, "{")
            print_ast(item.tag_content, level + 1)
            print("    " + "  " * level + "}")

