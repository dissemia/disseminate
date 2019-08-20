"""
Utilities for formatting html strings and text.
"""
from lxml.builder import E
from lxml import etree
from lxml.etree import Entity
from markupsafe import Markup

from .exceptions import FormattingError
from ..attributes import Attributes
from .. import settings


class HtmlFormatError(FormattingError):
    """Error in html formatting."""
    pass


def html_tag(name, attributes='', formatted_content=None, level=1,
             pretty_print=settings.html_pretty):
    """Format an html tag string.

    Parameters
    ----------
    name : Optional[str]
        The name of the html tag.
    attributes : Optional[Union[:obj:`Attributes <.Attributes>`, str]]
        The attributes of the tag.
    formatted_content : Optional[Union[str, list, :obj:`lxml.builder.E`]]
        The contents of the html tag.
    level : Optional[int]
        The level of the tag.
    pretty_print : Optional[bool]
        If True, make the formatted html pretty--i.e. with newlines and spacing
        for nested tags.

    Returns
    -------
    html : str
        If level=1, a string formatted in html
        if level>1, an html element (:obj:`lxml.build.E`)

    Raises
    ------
    HtmlFormatError : :exc:`HtmlFormatError`
        A TagError is raised if a non-allowed environment is used
    """
    # See if the tag is permitted
    allowed_tag = (name in settings.html_tag_arguments or
                   name in settings.html_tag_optionals)

    # Format the attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    if name in settings.html_tag_arguments:
        reqs = attributes.filter(attrs=settings.html_tag_arguments[name],
                                 target='html',
                                 sort_by_attrs=True)
    else:
        reqs = None

    # Make sure the correct number of required arguments were found
    if reqs is not None and len(reqs) != len(settings.html_tag_arguments[name]):
        msg = ("The html tag '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise HtmlFormatError(msg.format(name, reqs))

    # Get optional arguments
    if name in settings.html_tag_optionals:
        opts = attributes.filter(attrs=settings.html_tag_optionals[name],
                                 target='html',
                                 sort_by_attrs=True)
    else:
        opts = None

    # Prepare other attributes
    other = Attributes()

    # Wrap the formatted_content in a list and remove empty strings
    formatted_content = ([formatted_content]
                         if not isinstance(formatted_content, list) else
                         formatted_content)
    formatted_content = [i for i in formatted_content
                         if i != '' and i is not None]

    # Create the tag
    if not allowed_tag:
        # Append the name as a class to the span element
        other['class'] = name

        # If the tag isn't listed in the 'allowed' tags, just create a span
        # element.
        e = E('span', *formatted_content) if formatted_content else E('span')
    else:
        e = E(name, *formatted_content) if formatted_content else E(name)

    # Add the reqs and opts attributes
    for attrs in (i for i in (reqs, opts, other) if i is not None):
        for k, v in attrs.items():
            e.set(k, v)

    # Format the tag into a string, if it's the root level
    if level == 1:
        s = (etree.tostring(e, pretty_print=pretty_print)
                  .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return e


def html_entity(entity, level=1, pretty_print=settings.html_pretty):
    """Format an html entity string.

    Parameters
    ----------
    entity : str
        an html entity string
    level : Optional[str]
        The level of the tag.
    pretty_print : Optional[bool]
        If True, make the formatted html pretty--i.e. with newlines and spacing
        for nested tags.

    Returns
    -------
    html : str
        The entity formatted in html.

    Examples
    --------
    >>> html_entity('alpha')
    Markup('&alpha;\\n')

    Raises
    ------
    ValueError
        Raised for an invalid entity reference
    TagError
        Raised if the contents of the tag aren't a simple string. i.e. nested
        tags are not allowed.
    """
    if not isinstance(entity, str):
        msg = "The tag content '{}' cannot be translated into an html entity"
        raise HtmlFormatError(msg.format(str(entity)))

    e = Entity(entity.strip())
    if level == 1:
        s = (etree.tostring(e, pretty_print=pretty_print)
             .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return e