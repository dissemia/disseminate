"""
Misc utilities for tags.
"""
from math import ceil
from copy import copy

from ..attributes import Attributes
from ..utils.types import StringPositionalValue


def content_to_str(content, target='.txt', **kwargs):
    """Convert a tag or string to a string for the specified target.

    This function is used to convert an element, which is either a string, tag
    or list of strings and tags, to a string.

    Parameters
    ----------
    content : Union[str, List[Union[str, list, :obj:`Tag \
        <disseminate.tags.tag.Tag>`], :obj:`Tag <disseminate.tags.tag.Tag>`]
        The element to convert into a string.
    target : str, optional
        The target format of the string to return.

    Returns
    -------
    formatted_str : str
        A string in the specified target format
    """
    target = target[1:] if target.startswith('.') else target  # rm leading '.'
    format_func = ('default_fmt' if target == 'txt' else
                   '_'.join((target, 'fmt')))  # ex: tex_fmt

    return ''.join(format_content(content=content, format_func=format_func,
                                  **kwargs))


def format_content(content, format_func, **kwargs):
    """Format the content using the format_func.

    Parameters
    ----------
    content : Union[str, List[Union[str, list, :obj:`Tag \
            <disseminate.tags.Tag>`]], optional
            The content to format
    format_func : str
        The name of the format_func to use. ex: 'tex_fmt'

    Returns
    -------
    content : str or list
        The content formatted using the specified format_func.
    """
    # Wrap content in a list and increment level
    content = [content] if not isinstance(content, list) else content

    content = [getattr(i, format_func)(**kwargs)
               if hasattr(i, format_func) else i for i in content]
    return content[0] if len(content) == 1 else content


def repl_tags(element, tag_class, replacement):
    """Replace all instances of a tag class with a replacement string.

    Parameters
    ----------
    element : Union[str, list :obj:`Tag <disseminate.tags.core.Tag>`]
        The element to replace tags with a replacement string.
    tag_class : :class:`Tag <disseminate.tags.core.Tag>`
        A tag class or subclass to replace.
    replacement : str
        The string to replace the tag with.
    """
    if isinstance(element, tag_class):
        return replacement
    elif hasattr(element, 'content'):
        element.content = repl_tags(element=element.content,
                                    tag_class=tag_class,
                                    replacement=replacement)
        return element
    elif isinstance(element, list):
        for i in range(len(element)):
            element[i] = repl_tags(element=element[i], tag_class=tag_class,
                                   replacement=replacement)

    return element


def replace_context(tag, new_context):
    """Replace the context for the given tag (and all subtags) to the given
    new_context.

    Parameters
    ----------
    tag : :obj:`Tag <disseminate.tags.core.Tag>`
        The tag to replace the context.
    new_context : :obj:`Type[BaseContext] <.context.BaseContext>`
        The new context to replace.
    """
    # Get all of the tags for the given tag
    flattened_tags = tag.flatten(filter_tags=True)

    # Replace the context for all tags
    for tag in flattened_tags:
        tag.context = new_context


def copy_tag(tag):
    """Create a copy of the given tag.

    The tag, attributes and content are deep copies, and the context points to
    the same context as the given tag.

    Parameters
    ----------
    tag : Union[str, list :obj:`Tag <disseminate.tags.core.Tag>`]
        The tag to copy.

    Returns
    -------
    tag_copy : :obj:`Tag <disseminate.tags.core.Tag>`
        The tag copy.
    """
    if isinstance(tag, str):
        # Do nothing for strings
        return tag
    if isinstance(tag, list):
        # Process each item in lists
        return [copy_tag(i) for i in tag]

    # At this point, the tag parameter should actually be a tag. First, copy
    # this tag
    tag_copy = copy(tag)  # shallow copy

    # make copies of the following fields. The __weakrefattrs__ dict needs
    # to be copied so that entries stored in it (like the context weak ref)
    # can be changed independently for the source and copied tags.
    for field in ('attributes', '__weakrefattrs__'):
        if hasattr(tag, field):
            value = getattr(tag, field)
            setattr(tag_copy, field, value.copy())

    # Copy its content
    tag_copy.content = copy_tag(tag_copy.content)

    return tag_copy


def percentage(value):
    """Given a strings (or floats or ints), convert into a float number between
    [0.0, 100.0].

    Parameters
    ----------
    value : Union[str, int, float]

    Returns
    -------
    percentage : Union[int, None]
        The percentage from 0 to 100, or
        None if the value could not be converted.

    Examples
    --------
    >>> percentage('10.2%')
    11
    >>> percentage('10.2')
    1020
    >>> percentage('0.3%')
    1
    >>> percentage('0.3')
    30
    >>> percentage(30)
    30
    """
    if isinstance(value, str):
        if '%' in value:
            try:
                value = float(value.strip().strip('%'))
            except ValueError:
                value = None
        else:
            try:
                value = float(value.strip()) * 100.0
            except ValueError:
                value = None

    try:
        return abs(ceil(value))
    except (ValueError, TypeError):
        return None


def tex_percentwidth(attributes, target='.tex', use_positional=False):
    """Generates an tex width string based on the 'width' entry in the
    attributes.

    Currently, this function works in halves (w50), thirds (w33, w66) and
    quarters (w25, w75)

    Parameters
    ----------
    attributes : :obj:`.attributes.Attributes`
        The attributes dict
    target : Optional[str]
        The target format to format the attribute dict for.
    use_positional : Optional[bool]
        Insert the entry as a positional attribute

    Returns
    -------
    attributes: :obj:`.attributes.Attributes`
        The same attributes dict with the width inserted as a
        StringPositionalArgument, if a width was found.

    Examples
    --------
    >>> tex_percentwidth('width=50%')
    Attributes{'width': '0.49\\\\textwidth'}
    >>> tex_percentwidth('width=3.2in')
    Attributes{'width': '3.2in'}
    >>> tex_percentwidth('width=50%', use_positional=True)
    Attributes{'width': '50%', \
'0.49\\\\textwidth': <class '...StringPositionalValue'>}
    """  # noqa: D301
    attributes = (Attributes(attributes)
                  if not isinstance(attributes, Attributes) else attributes)

    # Convert the width to a number between 0 and 100
    width = attributes.get('width', target=target)
    if width is None:
        return attributes

    percent_width = percentage(width)  # width from 0 to 100

    # Find which width window this falls in
    windows = {99: (75, 100),  # ]75, 100]
               74: (67, 75),
               65: (50, 67),
               49: (34, 50),
               32: (25, 33),
               24: (0, 25)}

    fit_percent_width = None
    if isinstance(percent_width, int):
        for test_percent_width, (range_min, range_max) in windows.items():
            if range_min < percent_width <= range_max:
                fit_percent_width = test_percent_width

    # Set the width value in the attributes dict
    if isinstance(fit_percent_width, int):
        str = "{}\\textwidth".format(fit_percent_width / 100.)
        if use_positional:
            attributes[str] = StringPositionalValue
        else:
            attributes['width'] = str
    else:
        str = "{}".format(width)
        if use_positional:
            attributes[str] = StringPositionalValue
        else:
            attributes['width'] = str

    return attributes


def xhtml_percentwidth(attributes, target='.html'):
    """Generates an (x)html class name based on the 'width' entry in the
    attributes.

    Currently, this function works in halves (w50), thirds (w33, w66) and
    quarters (w25, w75)

    Parameters
    ----------
    attributes : :obj:`.attributes.Attributes`
        The attributes dict
    target : Optional[str]
        The target format to format the attribute dict for.

    Returns
    -------
    attributes: :obj:`.attributes.Attributes`
        The same attributes dict with the 'class' entry set to an html class
        for the percent width, if a width was found.

    Examples
    --------
    >>> xhtml_percentwidth('width=50%')
    Attributes{'width': '50%', 'class': 'w50'}
    >>> xhtml_percentwidth('width=0%')  # None returned
    Attributes{'width': '0%'}
    """
    attributes = (Attributes(attributes)
                  if not isinstance(attributes, Attributes) else attributes)

    width = attributes.get('width', target=target)
    if width is None:
        return attributes

    percent_width = percentage(width)  # width from 0 to 100

    if not isinstance(percent_width, int):
        return attributes

    windows = {'w100': (75, 100),  # ]75, 100]
               'w75': (67, 75),
               'w66': (50, 67),
               'w50': (34, 50),
               'w33': (25, 33),
               'w25': (0, 25)}

    for html_class, (range_min, range_max) in windows.items():
        if range_min < percent_width <= range_max:
            cls_str = (attributes['class'] + ' ' + html_class
                       if 'class' in attributes else html_class)
            attributes['class'] = cls_str
            return attributes

    return attributes
