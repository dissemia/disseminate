"""
Misc utilities for tags.
"""
from .exceptions import TagError


def content_to_str(content, target='.txt'):
    """Convert a tag or string to a string for the specified target.

    This function is used to convert an element, which is either a string, tag
    or list of strings and tags, to a string.

    Parameters
    ----------
    content : str, :obj:`Tag <disseminate.tags.core.Tag>` or list of both
        The element to convert into a string.
    target : str, optional
        The target format of the string to return.

    Returns
    -------
    formatted_str : str
        A string in the specified target format
    """
    target = target.strip('.')  # remove leading period

    if isinstance(content, str):
        # if it's a string, we're good to go. Just return that, as it's just
        # what we need
        return content
    if hasattr(content, target):
        # if it's a tag with the target property (ex: tag.txt), then get that
        return getattr(content, target)
    if hasattr(content, 'txt'):
        # if it's a tag with the target a txt property then get that
        return getattr(content, 'txt')
    if isinstance(content, list):
        # if it's a list, process each item as a string or tag
        return ''.join(map(lambda x: content_to_str(x, target), content))

    msg = "Could not convert tag content '{}' to a string."
    raise TagError(msg.format(content))


def repl_tags(element, tag_class, replacement):
    """Replace all instances of a tag class with a replacement string.

    Parameters
    ----------
    element : str, list or :obj:`Tag <disseminate.tags.core.Tag>`
        The element to replace tags with a replacement string.
    tag_class : :class:`Tag <disseminate.tags.core.Tag>
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


# html targets

def set_html_tag_attributes(html_tag, attrs_dict):
    """Set the attributes for an html tag with the values in the given ordered
    dict.

    This function is needed to preserve the order of attributes set for an
    html tag. It is designed to be used with the lxml tag API.
    """
    for k, v in attrs_dict.items():
        html_tag.set(k, v)

