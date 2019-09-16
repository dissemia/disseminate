"""
Utilities for formatting tex strings and text.
"""
from .exceptions import FormattingError
from ..attributes import Attributes
from ..utils.string import space_indent
from .. import settings


class TexFormatError(FormattingError):
    """Error in latex formatting."""
    pass


def tex_cmd(cmd, attributes='', formatted_content=None, indent=None):
    """Format a tex command.

    Parameters
    ----------
    cmd : Optional[str]
        The name of the LaTeX command to format.
    attributes : Optional[Union[:obj:`Attributes <.Attributes>`, str]]
        The attributes of the tag.
    formatted_content : Optional[str]
        The contents of the tex environment formatted as a string in LaTeX.
        If not specified, the tex_str will not be used as a LaTeX parameter
    indent : Optional[int]
        If specified, indent lines by the given number of spaces.

    Returns
    -------
    tex_env : str
        The LaTeX environment string

    Raises
    ------
    TexFormatError : :exc:`TexFormatError`
        A TexFormatError is raised if an non-allowed environment is used.
    """
    # Make sure the environment is permitted
    if (cmd not in settings.tex_cmd_arguments and
       cmd not in settings.tex_cmd_optionals):
        msg = "Cannot use the LaTeX command '{}'"
        raise TexFormatError(msg.format(cmd))

    # Format the attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    if cmd in settings.tex_cmd_arguments:
        reqs = attributes.filter(attrs=settings.tex_cmd_arguments[cmd],
                                 sort_by_attrs=True, target='tex')
        reqs_str = reqs.tex_arguments
    else:
        reqs = None
        reqs_str = ''

    # Make sure the correct number of required arguments were found
    if (reqs is not None and
       len(reqs) != len(settings.tex_cmd_arguments[cmd])):
        msg = ("The LaTeX environment '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise TexFormatError(msg.format(cmd, reqs))

    # Get optional arguments
    if cmd in settings.tex_cmd_optionals:
        opts = attributes.filter(attrs=settings.tex_cmd_optionals[cmd],
                                 target='tex')
        opts_str = opts.tex_optionals
    else:
        opts_str = ''

    # Wrap the formatted_content in curly braces, if a formatted_content was
    # specified
    if isinstance(formatted_content, str):
        formatted_content = ("{" + formatted_content + "}"
                             if formatted_content else "{}")
    else:
        formatted_content = ''

    # format the tex command
    tex_text = "\\" + cmd + reqs_str + opts_str + formatted_content

    # Indent the text block, if specified
    if indent is not None:
        tex_text = space_indent(tex_text, number=indent)

    return tex_text


def tex_env(env, attributes, formatted_content, min_newlines=False,
            indent=None):
    """Format a tex environment.

    Parameters
    ----------
    env : str
        The name of the LaTeX environment to format.
    attributes : Union[:obj:`Attributes <.Attributes>`, str]
        The attributes of the tag.
    formatted_content : str
        The contents of the tex environment formatted as a string in LaTeX.
    min_newlines : Optional[bool]
        If True, extra new lines before, after and in the environment will not
        be included.
    indent : Optional[int]
        If specified, indent lines by the given number of spaces.

    Returns
    -------
    tex_env : str
        The LaTeX environment string

    Raises
    ------
    TexFormatError : :exc:`TexFormatError`
        A TexFormatError is raised if an non-allowed environment is used.
    """
    # Make sure the environment is permitted
    if (env not in settings.tex_env_arguments and
       env not in settings.tex_env_optionals):
        msg = "Cannot use the LaTeX environment '{}'"
        raise TexFormatError(msg.format(env))

    # Format the attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    # Get the required arguments
    if env in settings.tex_env_arguments:
        reqs = attributes.filter(attrs=settings.tex_env_arguments[env],
                                 target='tex',
                                 sort_by_attrs=True)
        reqs_str = reqs.tex_arguments
    else:
        reqs = None
        reqs_str = ''

    # Make sure the correct number of required arguments were found
    if (reqs is not None and
       len(reqs) != len(settings.tex_env_arguments[env])):
        msg = ("The LaTeX environment '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise TexFormatError(msg.format(env, reqs))

    # Get optional arguments
    if env in settings.tex_env_optionals:
        opts = attributes.filter(attrs=settings.tex_env_optionals[env],
                                 target='tex',
                                 sort_by_attrs=True)
        opts_str = opts.tex_optionals
    else:
        opts_str = ''

    # Add a leading and trailing new line to the formatted_content,
    # if there isn't one
    formatted_content = ('\n' + formatted_content
                         if not formatted_content.startswith('\n') else
                         formatted_content)
    formatted_content = (formatted_content + '\n'
                         if not formatted_content.endswith('\n') else
                         formatted_content)

    # format the tex environment
    tex_text = ("\\begin" + '{' + env + '}' +
                reqs_str +
                opts_str +
                (' %' if min_newlines else '') +
                formatted_content +
                "\\end{" + env + "}")

    # Indent the text block, if specified
    if indent is not None:
        tex_text = space_indent(tex_text, number=indent)

    # Add new_lines on the two ends of the block, if not min_newlines
    if not min_newlines:
        tex_text = "\n" + tex_text + "\n"

    return tex_text


def tex_verb(formatted_content):
    """Format a tex verb command

    Parameters
    ----------
    formatted_content : str
        The contents of the tex environment formatted as a string in LaTeX.

    Returns
    -------
    tex_verb : str
        The LaTeX verb string
    """
    assert isinstance(formatted_content, str)

    if '|' not in formatted_content:
        return "\\verb|" + formatted_content + "|"
    elif '!' not in formatted_content:
        return "\\verb!" + formatted_content + "!"
    elif '^' not in formatted_content:
        return "\\verb^" + formatted_content + "^"
    return formatted_content
