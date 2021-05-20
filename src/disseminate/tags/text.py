"""
Text formatting tags
"""
from html.entities import name2codepoint

from .tag import Tag
from .exceptions import TagError, assert_content_str
from ..formats import tex_cmd, tex_env, tex_verb, xhtml_entity, xhtml_tag
from .utils import format_content
from .. import settings


class Body(Tag):
    """A body tag for the body of a document.

    In (x)html, this is rendered as a <div> instead of the default <span>
    """

    active = True
    html_name = 'div'

    def html_fmt(self, attributes=None, **kwargs):
        attributes = attributes or self.attributes.copy()
        attributes['class'] = 'body'
        return super().html_fmt(attributes=attributes, **kwargs)

    def xhtml_fmt(self, content=None, attributes=None, format_func='xhtml_fmt',
                  method='xhtml', level=1, **kwargs):
        # Wrap the body tag in the epub namespace
        name = (self.html_name if self.html_name is not None else
                self.name.lower())

        # Collect the content elements
        content = content if content is not None else self.content
        content = format_content(content=content, format_func=format_func,
                                 level=level + 1)

        # Set the attributes
        attributes = attributes or self.attributes.copy()
        attributes['class'] = 'body'

        # Format the html tag
        return xhtml_tag(name=name, level=level, attributes=attributes,
                         formatted_content=content, method=method,
                         nsmap=settings.xhtml_namespace)


class P(Tag):
    """A Paragraph tag

    Attributes
    ----------
    active : bool
        This tag is active.
    include_paragraphs : bool
        The contents of this tag can be included in paragraphs.
    """
    active = True
    include_paragraphs = False

    def tex_fmt(self, **kwargs):
        tex = super(P, self).tex_fmt(**kwargs)

        # Rewrap the text
        # if settings.tex_paragraph_width > 0:
        #     tex = "\n".join(wrap(tex, settings.tex_paragraph_width))

        # Add newlines around paragraph if the content isn't a single tag
        # that is also a block
        if getattr(self.content, 'tex_paragraph_newlines', True):
            return "\n" + tex + "\n"
        else:
            return tex


class Bold(Tag):
    """A bold tag.

    Attributes
    ----------
    aliases : Tuple[str]
        A list of strs for other names a tag goes by
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_cmd : str
        Use this name to render the tex command.
    active : bool
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
    aliases : Tuple[str]
        A list of strs for other names a tag goes by
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_cmd : str
        Use this name to render the tex command.
    active : bool
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
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool
        This tag is active.
    """
    html_name = "sup"
    active = True

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        content = content if content is not None else self.content

        # Collect the content elements
        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        content = '^{' + content + '}'
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=content)
                if not mathmode else
                content)


class Sub(Tag):
    """A subscript tag.

    Attributes
    ----------
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool
        This tag is active.
    """
    html_name = "sub"
    active = True

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
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
    active : bool
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
            msg = ("The @supsub tag must contain only one element '&&' "
                   "element separator. "
                   "ex: @supsub{{superscript && subscript}}. The "
                   "tag given was: {}")
            raise TagError(msg.format(self))

        # Seperate the superscript and subscript
        sup, sub = self.content.split('&&')
        self._sup = sup.strip()
        self._sub = sub.strip()

    def html_fmt(self, content=None, attributes=None, format_func='html_fmt',
                 method='html', level=1, **kwargs):
        attrs = attributes or self.attributes.copy()
        attrs['class'] = 'supsub'
        br_tag = xhtml_tag(name='br', method=method, level=level + 1)
        return xhtml_tag(name='span', attributes=attrs,
                         formatted_content=[self._sup, br_tag, self._sub],
                         method=method, level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        formatted = "^{" + self._sup + "}_{" + self._sub + "}"
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=formatted)
                if not mathmode else
                formatted)


class Symbol(Tag):
    """One or more greek characters.

    Attributes
    ----------
    aliases : Tuple[str]
        A list of strs for other names a tag goes by
    active : bool, default: True
        This tag is active.
    """

    aliases = ("smb",)
    active = True

    def __init__(self, name, content, attributes, context):
        assert_content_str(content)
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        content = content if content is not None else self.content
        content = "\\" + content
        return (tex_cmd(cmd='ensuremath', attributes='',
                        formatted_content=content)
                if not mathmode else
                content)

    def html_fmt(self, content=None, attributes=None, method='html', level=1,
                 **kwargs):
        content = content or self.content
        return xhtml_entity(entity=content, method=method, level=level)

    def xhtml_fmt(self, content=None, attributes=None, method='xml', level=1,
                  **kwargs):
        content = (content or self.content).strip()

        # Convert the entity name to a code point, needed for epub.
        # ex: 'gamma' -> '#947'
        content = ('#' + str(name2codepoint[content])
                   if content in name2codepoint else content)
        return xhtml_entity(entity=content, method=method, level=level)


class Verb(Tag):
    """A verbatim tag for displaying unformatted blocks of text.

    Attributes
    ----------
    aliases : Tuple[str]
        A list of strs for other names a tag goes by
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    active : bool
        This tag is active.
    process_content : bool
        Do not process the contents of the tag--just take the contents
        literally.
    include_paragraphs : bool
        The contents of this tag cannot be included in paragraphs.
    """

    aliases = ("v", "pre", "verbatim")
    active = True

    process_content = False
    process_typography = False

    include_paragraphs = False

    html_name = 'code'

    def html_fmt(self, attributes=None, *args, **kwargs):
        attrs = attributes or self.attributes.copy()

        if self.name == "verbatim":
            attrs['class'] = 'block'
        return super(Verb, self).html_fmt(*args, **kwargs)

    def tex_fmt(self, *args, **kwargs):
        if self.name == "verbatim":
            return tex_env(env='verbatim', attributes='',
                           formatted_content=self.default_fmt())
        else:
            return tex_verb(self.default_fmt())
