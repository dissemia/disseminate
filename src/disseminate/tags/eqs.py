"""
Tags to render equations
"""
from copy import copy

from .tag import Tag
from .img import RenderedImg
from .processors.process_content import parse_tags
from ..attributes import Attributes


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
    """The inline equation tag

    Render an equation in native LaTeX or into a rendered SVG image using
    LaTeX.

    Attributes
    ----------
    aliases : list of str, default: ('term', 'termb')
        A list of strs for other names a tag goes by
    active : bool, default: True
        If True, the Tag can be used by the TagFactory.
    block_equation : bool
        If True, the equation will be rendered as a LaTeX block equation using
        a math environment. ex: \begin{equation}...\end{equation}
        If False, the equation will be rendered as a LaTeX inline equation.
        ex: "\ensuremath{y=x}
    """
    # TODO: "@eq[bold color=blue]{y=x}"

    aliases = ('term', 'termb')
    active = True

    process_content = False

    block_equation = None
    bold = None
    color = None

    _raw_content = None

    tex_format = "{content}"
    tex_inline_format = "\\ensuremath{{{content}}}"
    tex_block_format = ("\\begin{{{env}}}{attrs} %\n"
                        "{content}\n\\end{{{env}}}")
    default_block_env = "align*"

    def __init__(self, name, content, attributes, context,
                 block_equation=False):

        assert context.is_valid('equation_renderer')
        self.block_equation = block_equation

        # Ensure the attributes argument is an Attributes type
        attributes = Attributes(attributes)

        # Get various properties from the attributes
        env = attributes.get('env', target='.tex')
        self.block_equation = (True if env is not None or
                               block_equation else False)
        self.env = env if env is not None else self.default_block_env

        bold = attributes.get('bold', target='.tex')
        self.bold = True if bold is not None or name == 'termb' else False

        self.color = attributes.get('color', target='.tex')

        # Remove these properties from the attributes, as they're no longer
        # needed and should be included when formatting tags
        attributes = attributes.exclude(('env', 'bold', 'color'))

        # Save the raw content and raw attributes and format the content in tex
        # The content for this tag will be replaced by the path of the image
        # by RenderImg
        content = parse_tags(content=content, context=context)
        self._raw_content = content
        self.attributes = attributes
        content = self.tex

        # Note: This crop command should not cut off baselines such that
        # equation images won't line up properly with the surrounding text.
        # ex: H vs Hy
        #
        # Crop equation images created by the dependency manager. This removes
        # white space around the image so that the equation images.
        attributes['crop'] = (100, 100, 0, 0)

        super().__init__(name=name, content=content, attributes=attributes,
                         context=context, render_target='.tex')

    def render_content(self, content, context):
        """Render the content in LaTeX into a valid .tex file."""
        # Get the renderer for the equation
        renderer = context['equation_renderer']

        # Make a copy of the context and add the content as the 'body' entry.
        context_cp = copy(context)
        context_cp['body'] = content

        # Get the kwargs and args to pass to the template
        kwargs = self.template_kwargs()

        return renderer.render(context=context_cp, target='.tex', **kwargs)

    def html_fmt(self, level=1, content=None):
        if self.block_equation:
            self.attributes['class'] = 'eq blockeq'
        else:
            self.attributes['class'] = 'eq'
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
            if self.block_equation or self.paragraph_role == 'block':
                # Remove attributes that are not used for in the latex
                # formatting
                attrs = self.attributes.exclude('crop')

                attrs_str = attrs.tex
                attrs_str = '{' + attrs_str + '}' if attrs_str else attrs_str
                return self.tex_block_format.format(env=self.env,
                                                    attrs=attrs_str,
                                                    content=content)
            else:
                return self.tex_inline_format.format(content=content)
