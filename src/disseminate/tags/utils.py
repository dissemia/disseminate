"""
Misc utilities for tags.
"""
from copy import copy


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

    The tag, attributes and content are deep copies, and the context points to the
    same context as the given tag.

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

    # Copy its attributes
    tag_copy.attributes = tag.attributes.copy()

    # Copy its content
    tag_copy.content = copy_tag(tag_copy.content)

    return tag_copy
