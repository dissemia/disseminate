"""
Functions for processing Abstract Syntax Trees (ASTs).
"""
import regex

from ..tags import TagFactory, Tag
from .validate import ASTValidator
from . import settings


class AstException(Exception):
    """An error was encountered while processing the Abstract Syntax Tree"""
    pass


control_char = r'@'


re_tag = regex.compile(r'(@(?P<tag>[A-Za-z]\w*)'
                       r'(?P<attributes>\[[^\]]+\])?'
                       r'{(?P<content>(?>[^{}@]+|(?R))*)})')


def process_ast(ast=None, local_context=None, global_context=None,
                src_filepath=None, level=1):
    """Process an AST comprising a list of strings, lists or tags.

    .. note:: The AST processing should be able to reprocess the generated AST
              without making changes.

    .. warning:: The process_ast *can not* depend on the `local_context`
                 and `global_context` since these may not be fully populated
                 yet. However, it can populate these.

    Parameters
    ----------
    ast : list
        An optional AST to build from or a list of strings.
    local_context : dict, optional
        The context with values for the current document. (local)
    global_context : dict, optional
        The context with values for all documents in a project. (global)
    src_filepath : str, optional
        The path for the document (source markup) file being processed.
    level : int, optional
        The current level of the ast.

    Returns
    -------
    ast : :obj:`disseminate.Tag`
        The AST is a root tag with a content comprising a list of tags or
        strings.

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
    local_context = (local_context if isinstance(local_context, dict)
                     else dict())
    global_context = (global_context if isinstance(global_context, dict)
                      else dict())

    # Setup the parsing
    current_pos = 0
    factory = TagFactory()
    validator = ASTValidator(src_filepath=src_filepath)

    # Create the root ast. The passed argument can either be a list, or a
    # Tag for an already parsed root Tag
    if isinstance(ast, list):
        pass
    elif isinstance(ast, Tag):
        ast = ast.content
    else:
        ast = []
    new_ast = []

    for i in ast:

        # Each item should either be a string to be processed, or an
        # already-processed tag. If it's a tag, process its contents.
        if isinstance(i, str):
            s = i
        elif isinstance(i, Tag) and isinstance(i.content, str):
            s = i.content
        elif isinstance(i, Tag):
            i.content = process_ast(i.content, local_context, global_context,
                                    src_filepath, level + 1)
            new_ast.append(i)
            continue
        else:
            continue

        for m in re_tag.finditer(s):
            # Find the match's start and end positions in the string
            start, end = m.span()

            # Find the string up to this match and find the current line number
            string = s[current_pos:start]

            # Validate the string and match to make sure there are no errors.
            validator.validate(string, m)

            # Add the validated string to the ast
            new_ast.append(string)

            # Reset the current position to the end of this match
            current_pos = end

            # Parse the match's content
            d = m.groupdict()
            tag_name = m['tag']
            tag_content = process_ast([m['content']], local_context, global_context,
                                      src_filepath, level + 1)
            tag_attributes = m['attributes']

            if isinstance(i, Tag):
                i.content = tag_content
                i.attributes = tag_attributes
                new_ast.append(i)
            else:
                new_ast.append(factory.tag(tag_name=tag_name,
                                           tag_content=tag_content,
                                           tag_attributes=tag_attributes,
                                           local_context=local_context,
                                           global_context=global_context))

        # Add the end of the string, if it's valid
        string = s[current_pos:]
        validator.validate(string, None)
        if isinstance(i, Tag):
            i.content = string
            new_ast.append(i)
        else:
            new_ast.append(string)

    if level == 1:  # root level
        root = factory.tag(tag_name='root',
                           tag_content=new_ast,
                           tag_attributes=None,
                           local_context=local_context,
                           global_context=global_context)
        return root
    else:
        return new_ast