"""
Utilities for formatting tex strings and text.
"""
from ..exceptions import TagError
from ...attributes import Attributes
from ... import settings


def tex_cmd(cmd, attributes='', tex_str=None):
    """Format a tex command.

    Parameters
    ----------
    com : str, optional
        The name of the LaTeX command to format.
    attributes : :obj:`Attributes <diseeminate.attributes.Attributes>` or str
        The attributes of the tag.
    tex_str : str, optional
        The contents of the tex environment formatted as a string in LaTeX.
        If not specified, the tex_str will not be used as a LaTeX parameter

    Returns
    -------
    tex_env : str
        The LaTeX environment string

    Raises
    ------
    TagError
        A TagError is raised if:

        - an non-allowed environment is used
    """
    # Make sure the environment is permitted
    if cmd not in settings.tex_cmd_arguments:
        msg = "Cannot use the LaTeX command '{}'"
        raise TagError(msg.format(cmd))

    # Format the attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    reqs = attributes.filter(attrs=settings.tex_cmd_arguments[cmd],
                             target='tex')

    # Make sure the correct number of required arguments were found
    if len(reqs) != len(settings.tex_cmd_arguments[cmd]):
        msg = ("The LaTeX environment '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise TagError(msg.format(cmd, reqs))

    # Get optional arguments
    if cmd in settings.tex_cmd_optionals:
        opts = attributes.filter(attrs=settings.tex_cmd_optionals[cmd],
                                 target='tex')
        opts_str = opts.tex_optionals
    else:
        opts_str = ''

    # Wrap the tex_str in curly braces, if a tex_str was specified
    if isinstance(tex_str, str):
        tex_str = "{" + tex_str + "}" if tex_str else "{}"
    else:
        tex_str = ''

    # format the tex command
    return "\\" + cmd + reqs.tex_arguments + opts_str + tex_str


def tex_env(env, attributes, tex_str, min_newlines=False):
    """Format a tex environment.

    Parameters
    ----------
    env : str
        The name of the LaTeX environment to format.
    attributes : :obj:`Attributes <diseeminate.attributes.Attributes>` or str
        The attributes of the tag.
    tex_str : str
        The contents of the tex environment formatted as a string in LaTeX.
    min_newlines : bool, optional
        If True, extra new lines before, after and in the environment will not
        be included.

    Returns
    -------
    tex_env : str
        The LaTeX environment string

    Raises
    ------
    TagError
        A TagError is raised if:

        - an non-allowed environment is used
    """
    # Make sure the environment is permitted
    if env not in settings.tex_env_arguments:
        msg = "Cannot use the LaTeX environment '{}'"
        raise TagError(msg.format(env))

    # Format the attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    reqs = attributes.filter(attrs=settings.tex_env_arguments[env],
                             target='tex')

    # Make sure the correct number of required arguments were found
    if len(reqs) != len(settings.tex_env_arguments[env]):
        msg = ("The LaTeX environment '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise TagError(msg.format(env, reqs))

    # Get optional arguments
    if env in settings.tex_env_optionals:
        opts = attributes.filter(attrs=settings.tex_env_optionals[env],
                                 target='tex')
        opts_str = opts.tex_optionals
    else:
        opts_str = ''

        # format the tex environment
    if min_newlines:
        return ("\\begin" + '{' + env + '}' +
                reqs.tex_arguments +
                opts_str + ' %\n' +
                tex_str +
                "\n\\end{" + env + "}")
    else:
        return ("\n\\begin" + '{' + env + '}' +
                reqs.tex_arguments +
                opts_str + '\n' +
                tex_str +
                "\n\\end{" + env + "}\n")
