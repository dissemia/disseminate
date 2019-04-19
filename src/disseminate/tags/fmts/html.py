"""
Utilities for formatting html strings and text.
"""
from lxml.builder import E
from lxml import etree
from markupsafe import Markup

from ..exceptions import TagError
from ...attributes import Attributes
from ... import settings


def html_tag(name, level=1, attributes='', elements=None):
    """Format an html tag string.

    Parameters
    ----------
    name : str, optional
        The name of the html tag.
    level : int, optional
            The level of the tag.
    attributes : :obj:`Attributes <diseeminate.attributes.Attributes>` or str
        The attributes of the tag.
    elements : None, str, :obj:`lxml.builder.E` or list of both,  optional
        The contents of the html tag.

        The level of the tag.

    Returns
    -------
    html : str
        If level=1, a string formatted in html
        if level>1, an html element (:obj:`lxml.build.E)

    Raises
    ------
    TagError
        A TagError is raised if:

        - an non-allowed environment is used
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
                                 target='html')
    else:
        reqs = None

    # Make sure the correct number of required arguments were found
    if reqs is not None and len(reqs) != len(settings.html_tag_arguments[name]):
        msg = ("The html tag '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise TagError(msg.format(name, reqs))

    # Get optional arguments
    if name in settings.html_tag_optionals:
        opts = attributes.filter(attrs=settings.html_tag_optionals[name],
                                 target='html')
    else:
        opts = None

    # Prepare other attributes
    other = Attributes()

    # Wrap the elements in a list and remove empty strings
    elements = [elements] if not isinstance(elements, list) else elements
    elements = [i for i in elements if i != '' and i is not None]

    # Create the tag
    if not allowed_tag:
        # Append the name as a class to the span element
        other['class'] = name

        # If the tag isn't listed in the 'allowed' tags, just create a span
        # element.
        e = E('span', *elements) if elements else E('span')
    else:
        e = E(name, *elements) if elements else E(name)

    # Add the reqs and opts attributes
    for attrs in (i for i in (reqs, opts, other) if i is not None):
        for k, v in attrs.items():
            e.set(k, v)

    # Format the tag into a string, if it's the root level
    if level == 1:
        s = (etree.tostring(e, pretty_print=settings.html_pretty)
                  .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return e


    # if name in settings.html_valid_tags:
    #     # Create the html tag
    #     e = E(name, *elements) if elements else E(name)
    #
    #     # Set the attributes for the tag, in order.
    #     set_html_tag_attributes(html_tag=e, attrs_dict=attrs)
    # else:
    #     # Create a span element if it not an allowed element
    #     # Add the tag type to the class attribute
    #     attrs.append('class', name)
    #
    #     # Create the html tag
    #     e = E('span', *elements) if len(elements) else E('span')
    #
    #     # Set the attributes for the tag, in order.
    #     set_html_tag_attributes(html_tag=e, attrs_dict=attrs)
    #
    # # Render the root tag if this is the first level
    # if level == 1:
    #     s = (etree.tostring(e, pretty_print=settings.html_pretty)
    #          .decode("utf-8"))
    #     return Markup(s)  # Mark string as safe, since it's escaped by lxml
    # else:
    #     return e