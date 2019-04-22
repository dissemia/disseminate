"""
Text formatting tags
"""
from textwrap import wrap

from .tag import Tag, TagError
from ..formats import tex_cmd, tex_env, html_entity, html_tag
from .utils import format_content


class P(Tag):
    """A Paragraph tag

    Attributes
    ----------
    active : bool, default: True
        This tag is active.
    include_paragraphs : bool, default: False
        The contents of this tag can be included in paragraphs.
    """
    active = True
    include_paragraphs = False

    def tex_fmt(self, content=None, mathmode=False, level=1):
        tex = super(P, self).tex_fmt(content=content, mathmode=mathmode,
                                     level=level)

        # Rewrap the text
        # if settings.tex_paragraph_width > 0:
        #     tex = "\n".join(wrap(tex, settings.tex_paragraph_width))

        # Add newlines around headings
        return "\n" + tex + "\n"


class Bold(Tag):
    """A bold tag.

    Attributes
    ----------
    aliases : list of str, default: ("b", "textbf", "strong")
        A list of strs for other names a tag goes by
    html_name : str, default: "strong"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_cmd : str
        Use this name to render the tex command.
    active : bool, default: True
        This tag is active.
    """
    aliases = ("b", "textbf", "strong")
    html_name = "strong"
    tex_cmd = "textbf"
    active = True


class Italics(Tag):
    """An italics tag.

    Attributes
    ----------
    aliases : list of str, default: ("i", "textit")
        A list of strs for other names a tag goes by
    html_name : str, default: "i"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_cmd : str
        Use this name to render the tex command.
    active : bool, default: True
        This tag is active.
    """
    aliases = ("i", "textit")
    html_name = "i"
    tex_cmd = "textit"
    active = True


class Sup(Tag):
    """A superscript tag.

    Attributes
    ----------
    html_name : str, default: "sup"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    html_name = "sup"
    active = True

    def tex_fmt(self, content=None, mathmode=False, level=1):
        content = content if content is not None else self.content

        # Collect the content elements
        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        content = '^{' + content + '}'
        return (tex_cmd(cmd='ensuremath', attributes='', formatted_content=content)
                if not mathmode else
                content)


class Sub(Tag):
    """A subscript tag.

    Attributes
    ----------
    html_name : str, default: "sub"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    """
    html_name = "sub"
    active = True

    def tex_fmt(self, content=None, mathmode=False, level=1):
        content = content if content is not None else self.content

        # Collect the content elements
        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        content = '_{' + content + '}'
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=content)
                if not mathmode else
                content)


class Supsub(Tag):
    """A superscript/subscript tag, together, that displays them one on top of
    the other.

    The content of the tag consists of two elements separated by a '&&'
    character. ex: @supsub{superscript && subscript}

    Attributes
    ----------
    active : bool, default: True
        This tag is active.
    """
    active = True

    _sup = None
    _sub = None

    def __init__(self, *args, **kwargs):
        super(Supsub, self).__init__(*args, **kwargs)

        # Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @supsub tag cannot have tags nested within it."
            raise TagError(msg)

        # assert that the element separator, '&&', is in the contents
        if self.content.count('&&') != 1:
            msg = ("The @supsub tag must contain only one element '&&' element "
                   "separator. ex: @supsub{{superscript && subscript}}. The "
                   "tag given was: {}")
            raise TagError(msg.format(self))

        # Seperate the superscript and subscript
        sup, sub = self.content.split('&&')
        self._sup = sup.strip()
        self._sub = sub.strip()

    def html_fmt(self, content=None, level=1):
        attrs = self.attributes.copy()
        attrs['class'] = 'supsub'
        br_tag = html_tag(name='br', level=level + 1)
        return html_tag(name='span', attributes=attrs,
                        formatted_content=[self._sup, br_tag, self._sub],
                        level=level,)

    def tex_fmt(self, content=None, mathmode=False, level=1):
        formatted = "^{" + self._sup + "}_{" + self._sub + "}"
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=formatted)
                if not mathmode else
                formatted)


class Symbol(Tag):
    """One or more greek characters.

    Attributes
    ----------
    aliases : list of str, default: ("smb",)
        A list of strs for other names a tag goes by
    active : bool, default: True
        This tag is active.
    """

    aliases = ("smb ",)
    active = True

    def assert_not_nested(self):
        """Raise a TagError if this tag is nested."""
        if not isinstance(self.content, str):
            msg = "The @symbol tag cannot have tags nested within it."
            raise TagError(msg)

    def html_fmt(self, content=None, level=1):
        self.assert_not_nested()
        return html_entity(entity=self.content, level=level)

    def tex_fmt(self, content=None, mathmode=False, level=1):
        content = content if content is not None else self.content
        self.assert_not_nested()
        content = "\\" + content
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=content)
                if not mathmode else
                content)


class Verb(Tag):
    """A verbatim tag for displaying unformatted blocks of text.

    Attributes
    ----------
    aliases : list of str, default: ("v", "pre", "verbatim")
        A list of strs for other names a tag goes by
    html_name : str, default: "code"
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool, default: True
        This tag is active.
    process_content : bool, optional
        Do not process the contents of the tag--just take the contents
        literally.
    include_paragraphs : bool, default: False
        The contents of this tag cannot be included in paragraphs.
    """

    aliases = ("v", "pre", "verbatim")
    active = True

    process_content = False
    process_typography = False

    include_paragraphs = False

    html_name = 'code'

    def __init__(self, name, content, attributes, context):
        super().__init__(name, content, attributes, context)

    def html_fmt(self, content=None, level=1):
        if self.name == "verbatim":
            self.attributes['class'] = 'block'
        return super(Verb, self).html_fmt(content=content, level=level + 1)

    def tex_fmt(self, *args, **kwargs):
        if self.name == "verbatim":
            return tex_env(env='verbatim', attributes='',
                           formatted_content=self.default_fmt())
        else:
            return "\\verb|" + self.default_fmt() + "|"
