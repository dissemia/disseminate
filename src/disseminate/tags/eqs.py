"""
Equation tags.
"""
from .core import Tag
from .img import RenderedImg
from ..attributes import (set_attribute, remove_attribute, get_attribute_value,
                          format_tex_attributes)


def raw_content_string(content):
    """Generate a string from the content."""
    if isinstance(content, str):
        return content

    elif isinstance(content, list) or hasattr(content, '__iter__'):
        return ''.join(map(raw_content_string, content))

    elif isinstance(content, Tag) and hasattr(content, 'tex'):
        return content.tex_fmt(mathmode=True)

    elif hasattr(content, 'content'):
        return raw_content_string(content.content)

    else:
        return ""


class Eq(RenderedImg):
    """The inline equation tag"""
    # TODO: "@eq[bold color=blue]{y=x}"

    aliases = ('term', 'termb')
    src_filepath = None
    active = True

    block_equation = None
    bold = None
    color = None

    _raw_content = None
    _raw_attributes = None

    tex_format = "{content}"
    tex_inline_format = "\\ensuremath{{{content}}}"
    tex_block_format = ("\\begin{{{env}}}{attrs} %\n"
                        "{content}\n\\end{{{env}}}")
    default_block_env = "align*"

    def __init__(self, name, content, attributes, context,
                 block_equation=False):
        assert context.is_valid('equation_renderer')
        self.block_equation = block_equation

        # Set the equation template for rendering pdf/svg versions of equations
        renderer = context['equation_renderer']
        eq_template = renderer.get_template(target='.tex')

        # Get the environment type
        env = get_attribute_value(attributes, attribute_name='env',
                                  target='.tex')
        attributes = remove_attribute(attributes, 'env')

        # If the env attribute is specified, then it must be a block environment
        if env:
            self.block_equation = True
        self.env = env if env is not None else self.default_block_env

        # Determine if bold
        bold = get_attribute_value(attributes, attribute_name='bold',
                                   target='.tex')
        attributes = remove_attribute(attributes, 'bold')
        if bold or name == 'termb':
            self.bold = True
        else:
            self.bold = False

        # Determine if a color was specified
        color = get_attribute_value(attributes, attribute_name='color',
                                   target='.tex')
        attributes = remove_attribute(attributes, 'color')
        self.color = color

        # Save the raw content and raw attributes and format the content in tex
        self._raw_attributes = attributes
        self._raw_content = content
        content = self.tex

        super(Eq, self).__init__(name=name, content=content,
                                 attributes=attributes,
                                 context=context,
                                 render_target='.tex',
                                 template=eq_template)

    def html_fmt(self, level=1, content=None):
        if self.block_equation:
            self.attributes = set_attribute(self.attributes,
                                            ('class', 'eq blockeq'))
        else:
            self.attributes = set_attribute(self.attributes,
                                            ('class', 'eq'))
        return super(Eq, self).html_fmt(level, content)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        raw_content = raw_content_string(self._raw_content).strip(' \t\n')
        content = raw_content

        # Add bold and color if specified
        if self.color:
            content = "\\textcolor{" + self.color + "}{" + content + "}"
        if self.bold:
            content = "\\boldsymbol{" + content + "}"

        if mathmode:
            return content
        else:
            if self.block_equation:
                attrs = format_tex_attributes(self._raw_attributes,
                                              left_bracket="{",
                                              right_bracket="}")
                return self.tex_block_format.format(env=self.env, attrs=attrs,
                                                    content=content)
            else:
                return self.tex_inline_format.format(content=content)
