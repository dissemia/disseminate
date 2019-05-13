"""
Function(s) to make typographic substitutions.
"""
import regex

from .process_tag import ProcessTag


class ProcessTypography(ProcessTag):
    """A tag processor to identify and format typography in tags.

    The contents of tags will be processed if the tag's
    :attr:`process_typography <disseminate.Tags.Tag.process_content>`
    attribute is True.
    """

    order = 300
    short_desc = "Identify and replace typographic characters, like endashes"

    def __call__(self, tag):
        process_typography(tag, tag_base_cls=self.tag_base_cls)


re_endash = regex.compile(r"[\s\u00a0]*(--|\u2013)[\s\u00a0]*")
re_emdash = regex.compile(r"[\s\u00a0]*(---|\u2014)[\s\u00a0]*")
re_apostrophe = regex.compile(r"(?<=\w)'(?=\w)")
re_single_start = regex.compile(r"(?<!\w)'(?=\S)")
re_single_end = regex.compile(r"(?<=\S)'(?!\w)")
re_double_start = regex.compile(r"(?<!\w)\"(?=\S)")
re_double_end = regex.compile(r"(?<=\S)\"(?!\w)")


def process_typography(tag, tag_base_cls, level=1):
    """Process the typography for an AST.

    .. note:: This function should be run after process_ast.

    Parameters
    ----------
    tag : Union[str, list]
        A string to parse into an AST, a list of strings or an existing AST.
    tag_base_cls : :class:`Tag <disseminate.tags.tag.Tag>`
        The base class for Tag objects.
    level : Optional[int]
        The current level of the tag.

    Returns
    -------
    tag : :obj:`disseminate.Tag`
        The AST is a root tag with a content comprising a list of tags or
        strings.
    """
    if isinstance(tag, str):
        # Process the tag if it's simply a string
        tag = re_emdash.sub('\u2014', tag)
        tag = re_endash.sub('\u2013', tag)
        tag = re_apostrophe.sub('’', tag)
        tag = re_single_start.sub('‘', tag)
        tag = re_single_end.sub('’', tag)
        tag = re_double_start.sub('“', tag)
        tag = re_double_end.sub('”', tag)
        return tag

    elif (isinstance(tag, tag_base_cls) and
          getattr(tag, 'process_typography', False)):
        # Process the tag contents
        tag.content = process_typography(tag=tag.content,
                                         tag_base_cls=tag_base_cls,
                                         level=level + 1)
        return tag

    elif isinstance(tag, list):
        # Process each element of lists
        for i, element in enumerate(tag):
            tag[i] = process_typography(tag=element,
                                        tag_base_cls=tag_base_cls,
                                        level=level + 1)

    return tag
