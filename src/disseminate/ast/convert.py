"""
Functions and classes to convert an AST to a target format.
"""
from lxml.builder import E
from lxml import etree

from disseminate.tags import Tag
from disseminate.attributes import kwargs_attributes
from . import settings


def convert(ast):
    """Converts and AST to txt.

    This method simply returns the contents of tags.

    .. warning:: The conversion method can read and depend on the
                 `local_context` and `global_context`, but it should not write
                 to them.

    Parameters
    ----------
    local_context : dict, optional
        The context with values for the current document. The values in this
        dict do not depend on values from other documents. (local)
    global_context : dict, optional
        The context with values for all documents in a project. The
        `global_context` is constructed with the `src_filepath` as a key and
        the `local_context` as a value.

    Returns
    -------
    txt_str : str
        A processed txt string.
    """
    if isinstance(ast, Tag):
        if isinstance(ast.content, list):
            return "".join(*[convert(i) for i in ast.content])
        else:
            return ast.content
    elif isinstance(ast, list):
        return "".join(*ast)
    else:
        return ast


def convert_html(ast, root_tag=settings.html_root_tag,
                 pretty_print=settings.html_pretty):
    """Converts an AST to html.

    .. warning:: The conversion method can read and depend on the
                 `local_context` and `global_context`, but it should not write
                 to them.

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


def convert_html(ast, root_tag=settings.html_root_tag,
                 pretty_print=settings.html_pretty):
    """Converts an AST to html.

    .. warning:: The conversion method can read and depend on the
                 `local_context` and `global_context`, but it should not write
                 to them.

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
    # Add a new line to the end, if needed
    elements = [i.html() if hasattr(i, 'html') else i for i in ast]

    # Fix new lines
    if (not isinstance(elements[-1], str) or
        elements[-1] and elements[-1][-1] != '\n'):
        elements.append('\n')

    return etree.tostring(E(root_tag, *elements),
                          pretty_print=pretty_print).decode("utf-8")


conversions = {
    'detault': convert,
    '.html': convert_html}