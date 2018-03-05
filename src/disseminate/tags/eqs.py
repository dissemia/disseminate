"""
Equation tags.
"""
from .core import Tag
from .img import RenderedImg
from ..attributes import set_attribute
from . import settings


def raw_content_string(content):
    """Generate a string from the content."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list) or hasattr(content, '__iter__'):
        return ''.join(map(raw_content_string, content))
    elif isinstance(content, Eq) and hasattr(content, '_raw_content'):
        raw_content = raw_content_string(content._raw_content)

        return (content.tex_format.format(content=raw_content)
                if hasattr(content, 'tex_format')
                else raw_content)

    elif hasattr(content, 'content'):
        return raw_content_string(content.content)
    else:
        return ""


class Eq(RenderedImg):
    """The inline equation tag"""
    # TODO: Images shouldn't be converted on creation

    aliases = ('term',)
    src_filepath = None
    active = True

    block_equation = None
    _raw_content = None
    tex_format = "{content}"
    tex_inline_format = "\\ensuremath{{{content}}}"
    tex_block_format = "\\begin{{{env}}}\n{{{content}}}\n\\end{{{env}}}"
    default_block_env = "align*"

    def __init__(self, name, content, attributes,
                 local_context, global_context, block_equation=False,
                 eq_template=None):
        self.block_equation = block_equation

        # Set the equation template for rendering pdf/svg versions of equations
        eq_template = 'eq' if eq_template is None else eq_template

        # Add css class for html formatting
        attributes = set_attribute(attributes, ('class', 'eq'))

        # Save the raw content and format the content in tex
        self._raw_content = content
        content = self.tex()

        super(Eq, self).__init__(name=name, content=content,
                                 attributes=attributes,
                                 local_context=local_context,
                                 global_context=global_context,
                                 render_target='.tex',
                                 template=eq_template)

    def tex(self, level=1):
        raw_content = raw_content_string(self._raw_content)
        raw_content.strip('\n')
        content = self.tex_format.format(content=raw_content)

        if self.block_equation:
            env = self.default_block_env
            return self.default_block_env.format(env=env, content=content)
        else:
            return self.tex_inline_format.format(content=content)


class EqBold(Eq):
    """A bolded inline equation."""

    aliases = ('termb',)

    tex_format = "\\boldsymbol{{{content}}}"
