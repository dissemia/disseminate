"""
Utilities for formatting html strings and text.
"""
from itertools import groupby

from lxml.builder import E, ElementMaker
from lxml import etree
from lxml.etree import Entity
from markupsafe import Markup

from .exceptions import FormattingError
from ..attributes import Attributes
from .. import settings


class XHtmlFormatError(FormattingError):
    """Error in xhtml formatting."""
    pass


def html_tag(*args, **kwargs):
    return html_tag(*args, **kwargs, method='html')


def xml_tag(*args, **kwargs):
    return xhtml_tag(*args, **kwargs, method='xml')


def xhtml_tag(name, attributes=None, formatted_content=None, level=1,
              target=None, method='html', nsmap=None,
              pretty_print=settings.xhtml_pretty):
    r"""Format an xhtml tag string.

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
    target : Optional[str]
        If speficied, filter the attributes that match the given target.
    method : Optional[str]
        The rendering method. 'html', 'xhtml' or 'xml'
    nsmap : Optional[dict]
        Optional namespace map to create the tag with.
    pretty_print : Optional[bool]
        If True, make the formatted html pretty--i.e. with newlines and spacing
        for nested tags.

    Returns
    -------
    html : str
        If level=1, a string formatted in (x)html
        if level>1, an html element (:obj:`lxml.build.E`)

    Raises
    ------
    XHtmlFormatError : :exc:`XHtmlFormatError`
        A TagError is raised if a non-allowed environment is used

    Examples
    --------
    >>> xhtml_tag('img', attributes="src='test.svg'")
    Markup('<img src="test.svg">\n')
    >>> xhtml_tag('img', attributes="src='test.svg'", method='xml')
    Markup('<img src="test.svg"/>\n')
    """
    method = 'xml' if method == 'xhtml' else method

    # See if the tag is permitted
    allowed_tag = (name in settings.xhtml_tag_arguments or
                   name in settings.xhtml_tag_optionals)

    # Format the attributes
    attributes = '' if attributes is None else attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Get the required arguments
    if name in settings.xhtml_tag_arguments:
        # If it's an allowed tag, get the required arguments for that tag
        reqs = attributes.filter(attrs=settings.xhtml_tag_arguments[name],
                                 target=target, sort_by_attrs=True)
    elif not allowed_tag and 'span' in settings.xhtml_tag_arguments:
        # If it's not an allowed tag, use a 'span' tag and its required
        # arguments
        reqs = attributes.filter(attrs=settings.xhtml_tag_arguments['span'],
                                 target=target, sort_by_attrs=True)
    else:
        reqs = None

    # Make sure the correct number of required arguments were found
    if (reqs is not None and
       len(reqs) != len(settings.xhtml_tag_arguments[name])):
        msg = ("The html tag '{}' did not receive the correct "
               "required arguments. Required arguments received: {}")
        raise XHtmlFormatError(msg.format(name, reqs))

    # Get optional arguments
    if name in settings.xhtml_tag_optionals:
        # If it's an allowed tag, get the optional arguments for that tag
        opts = attributes.filter(attrs=settings.xhtml_tag_optionals[name],
                                 target=target, sort_by_attrs=True)
    elif not allowed_tag and 'span' in settings.xhtml_tag_optionals:
        # If it's not an allowed tag, use a 'span' tag and its optional
        # arguments
        opts = attributes.filter(attrs=settings.xhtml_tag_optionals['span'],
                                 target=target, sort_by_attrs=True)
    else:
        opts = None

    # Prepare other attributes
    other = Attributes()

    # Wrap the formatted_content in a list
    formatted_content = ([formatted_content]
                         if not isinstance(formatted_content, list) else
                         formatted_content)

    # Clean up the formatted contents
    new_formatted_content = []
    for element in formatted_content:
        # Remove empty items
        if element == '' or element is None:
            continue

        # Format safe content into an Html element
        if isinstance(element, Markup):
            element = etree.fromstring(element)

        # Append the item to the new list
        new_formatted_content.append(element)

    formatted_content.clear()
    formatted_content += new_formatted_content

    # Create the tag
    # Create the element maker with a namespace, if needed
    EM = E if nsmap is None else ElementMaker(nsmap=nsmap)

    if not allowed_tag:
        # Append the name as a class to the span element, if a class hasn't
        # been specified
        if (reqs is not None and 'class' in reqs or
           opts is not None and 'class' in opts):
            pass
        else:
            other['class'] = name

        # If the tag isn't listed in the 'allowed' tags, just create a span
        # element.
        e = EM('span', *formatted_content) if formatted_content else E('span')
    else:
        e = EM(name, *formatted_content) if formatted_content else E(name)

    # Add the reqs and opts attributes
    for attrs in (i for i in (reqs, opts, other) if i is not None):
        for k, v in attrs.items():
            if v is None:
                continue
            e.set(k, v)

    # Format the tag into a string, if it's the root level
    if level == 1:
        s = (etree.tostring(e, pretty_print=pretty_print, method=method)
                  .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return e


def xml_entity(*args, **kwargs):
    return xhtml_entity(*args, **kwargs, method='xml')


def xhtml_entity(entity, level=1, method='html',
                 pretty_print=settings.xhtml_pretty):
    r"""Format an html entity string.

    Parameters
    ----------
    entity : str
        an html entity string
    level : Optional[str]
        The level of the tag.
    method : Optional[str]
        The rendering method. 'html', 'xhtml' or 'xml'
    pretty_print : Optional[bool]
        If True, make the formatted html pretty--i.e. with newlines and spacing
        for nested tags.

    Returns
    -------
    xhtml : str
        The entity formatted in xhtml.

    Raises
    ------
    XHtmlFormatError
        Raised if the contents of the tag aren't a simple string. i.e. nested
        tags are not allowed.

    Examples
    --------
    >>> xhtml_entity('alpha')
    Markup('&alpha;\n')
    """
    method = 'xml' if method == 'xhtml' else method

    if not isinstance(entity, str):
        msg = "The tag content '{}' cannot be translated into an html entity"
        raise XHtmlFormatError(msg.format(str(entity)))

    e = Entity(entity.strip())
    if level == 1:
        s = (etree.tostring(e, pretty_print=pretty_print, method=method)
             .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return e


def xhtml_list(*elements, attributes=None, listtype='ol', level=1,
               target=None, method='html', pretty_print=settings.xhtml_pretty,
               inner=False):
    """
    A xhtml list element.

    Parameters
    ----------
    elements : Tuple[Tuple[int, :obj:`lxml.builder.E`]]
        Each element is a tuple of the list element level and the 'li' lxml
        element.
    attributes : Optional[Union[:obj:`Attributes <.Attributes>`, str]]
        The attributes of the tag.
    listtype : Optional[str]
        The type of list to create. ex: ul, ol
    level : Optional[int]
        The level of the tag.
    target : Optional[str]
        If speficied, filter the attributes that match the given target.
    method : Optional[str]
        The rendering method. 'html', 'xhtml' or 'xml'
    pretty_print : Optional[bool]
        If True, make the formatted html pretty--i.e. with newlines and spacing
        for nested tags.
    inner : Optional[bool]
        If True, this function is invoked as an inner html list. This is
        useful for adding html attributes only to the outer list.

    Returns
    -------
    xhtml : str
        If level=1, a string formatted in html
        if level>1, an html element (:obj:`lxml.build.E`)

    Raises
    ------
    XHtmlFormatError : :exc:`HtmlFormatError`
        A TagError is raised if a non-allowed list environment is used
    """
    method = 'xml' if method == 'xhtml' else method

    current_elements = []
    listlevel = elements[0][0] if elements else 0

    _count = 0

    # Setup a counter function for list levels. When a new list item is
    # encountered, all sub items will receive the same number so that they're
    # grouped together.
    def counter(item):
        nonlocal _count
        if item[0] == listlevel:
            _count += 1
        return _count

    # Go by each list item and its group of sublists
    for is_same_list, group in groupby(elements, counter):
        group = list(group)

        # Add the parent list item
        current_elements.append(group[0][1])

        # If there are sub list items, add these as well
        if group[1:]:
            lst = xhtml_list(*group[1:], listtype=listtype, level=level + 1,
                             target=target, method=method,
                             pretty_print=pretty_print, inner=True)
            current_elements.append(lst)

    # Wrap current_elements in a list
    attributes = attributes if not inner else ''
    if level == 1:
        e = xhtml_tag(name=listtype, formatted_content=current_elements,
                      attributes=attributes, level=level + 1, target=target,
                      method=method, pretty_print=pretty_print)
        s = (etree.tostring(e, pretty_print=pretty_print, method=method)
             .decode("utf-8"))
        return Markup(s)  # Mark string as safe, since it's escaped by lxml
    else:
        return xhtml_tag(name=listtype, formatted_content=current_elements,
                         attributes=attributes, level=level + 1, target=target,
                         method=method, pretty_print=pretty_print)
