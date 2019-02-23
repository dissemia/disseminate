"""
Utilities for tags.
"""


def set_html_tag_attributes(html_tag, attrs_dict):
    """Set the attributes for an html tag with the values in the given ordered
    dict.

    This function is needed to preserve the order of attributes set for an
    html tag. It is designed to be used with the lxml tag API.
    """
    for k, v in attrs_dict.items():
        html_tag.set(k, v)


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
