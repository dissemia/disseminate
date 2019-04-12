"""
Tag processors for parsing the string contents of tags into a tree of tags.
(an Abstract Syntax Tree)
"""
import regex

from .process_tag import ProcessTag
from ..exceptions import TagError
from ..factory import TagFactory
from ..tag import Tag
from ...utils.string import group_strings
from ... import settings

re_open_tag = regex.compile(  # The character to use in identifying a tag. By
                              # default, it's an '@' character.
                                settings.tag_prefix +
                                r'(?P<tag>[A-Za-z0-9][\w]*)'
                                r'(?P<attributes>\[[^\]]+\])?'
                                r'(?P<open>{)?')
re_brace = regex.compile(r'[}{]')


class ProcessContent(ProcessTag):
    """The the tag processor for the contents of tags.

    The contents of tags will be processed if the tag's :attr:`process_content
    <disseminate.Tags.Tag.process_content>` attribute is True.
    """

    order = 200
    short_desc = "Parse tags in the contents of tags and strings"

    def __call__(self, tag):
        if tag.process_content:
            content = parse_tags(content=tag.content, context=tag.context)
            tag.content = content


def parse_tags(content, context, level=1):
    """Process a string into a tree of tags, strings and lists of both.

    .. note:: The parsing of tags is idempotent. It will reprocess the
              generated tag without making changes.

    Parameters
    ----------
    content : str or list
        A string to parse for tags, a list of strings and tags
    context : dict
        The context with values for the document.
    level : int, optional
        The current level of the ast.

    Returns
    -------
    tag_list : list of strings and tags

    Raises
    ------
    TagError
        Raises an TagError if the max depth has been achieved
        (settings.tag_max_depth). This is an attempt to foil the Billion Laughs
        attack.
    """
    # Conduct initial tests
    if level >= settings.tag_max_depth:
        msg = ("The maximum depth of '{}' has been reached in the Tag tree. "
               "Additional levels can be set by the 'settings.tag_max_depth'.")
        raise TagError(msg.format(settings.tag_max_depth))

    new_content = []
    parse = lambda x: parse_tags(x, context, level + 1)

    # Look at the element and process it depending on whether it's a string, tag
    # or list
    if isinstance(content, str):
        pass
    elif isinstance(content, list):
        return list(map(parse, content))
    elif isinstance(content, Tag):
        if (isinstance(content.content, str) or
           isinstance(content.content, Tag)):
            content.content = parse(content.content)
        elif isinstance(content.content, list):
            content.content = list(map(parse, content.content))
        return content
    else:
        msg = "Tag content in an unknown format. The tag contents are: {}"
        raise TagError(msg.format(content))

    # The following only processes text
    text = content

    # Setup the tag factor to generate tags
    factory = TagFactory(base_tag_class=Tag)

    # The parser starts at the start of the text string
    position = 0

    # find open tags
    match_tag = re_open_tag.search(text[position:])

    # Process the tag
    while match_tag:
        # Add the text up to this tag the match start/end are relative to the
        # truncated text[position:] string, so the match start position has
        # to be offset when referencing the full 'text' string
        match_tag_start = position + match_tag.start()
        sofar = text[position:match_tag_start]  # the string up to this point
        if sofar:  # only add the sofar string if it isn't an empty string
            new_content.append(sofar)

        # Push up the position to the end of the tag match
        position += match_tag.end()
        start_position = position

        # Parse the tag contexts
        d = match_tag.groupdict()
        tag_name = d['tag']
        tag_attributes = d['attributes']

        # Find open and close braces and advance the position
        # up until the match closing brace is found
        brace_level = 1 if d['open'] is not None else 0
        match = re_brace.search(text[position:])
        while match and 0 < brace_level < 10:
            # Increment or decrement the match
            if match.group() == '}':
                brace_level -= 1
            elif match.group() == '{':
                brace_level += 1

            position += match.end()

            # Get the next match
            match = re_brace.search(text[position:])

        # Raise an error if the brace wasn't closed
        if brace_level > 0:
            msg = "The tag '{}' was not closed."
            raise TagError(msg.format(tag_name))

        # Parse the ast for the tag's content
        if d['open'] is None:
            # For tags with no open/close braces, then the content is empty
            tag_content = ''

        else:
            # Otherwise process the text within the tag's braces
            inner_text = text[start_position:position - 1]

            # Process the inner_text if it's more than the empty string
            tag_content = inner_text if inner_text else ''

        tag = factory.tag(tag_name=tag_name,
                          tag_content=tag_content,
                          tag_attributes=tag_attributes,
                          context=context, )
        new_content.append(tag)

        # Find the next tag
        match_tag = re_open_tag.search(text[position:])

    # Add the remainer
    remainder = text[position:]
    if remainder:  # only add the remainder if it isn't an empty string
        new_content.append(remainder)

    # Remove empty strings
    group_strings(new_content)

    # Simplify the new_content list
    if len(new_content) == 1:
        # Unwrap new_content if it's a list with only one item
        new_content = new_content[0]
    elif len(new_content) == 0:
        # If the new_content list has no items, then just use an empty string
        new_content = ''

    return new_content