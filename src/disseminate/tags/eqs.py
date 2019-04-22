"""
Tags to render equations
"""
from copy import copy

from .tag import Tag
from .img import RenderedImg
from .processors.process_content import parse_tags
from ..formats import tex_cmd, tex_env
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
        self.tex_env = env if env is not None else self.default_block_env

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

    def html_fmt(self, content=None, level=1):
        if self.block_equation:
            self.attributes['class'] = 'eq blockeq'
        else:
            self.attributes['class'] = 'eq'
        return super(Eq, self).html_fmt(content=content, level=level)

    def tex_fmt(self, content=None, mathmode=False, level=1):
        raw_content = raw_content_string(self._raw_content).strip(' \t\n')
        content = raw_content

        # Add bold and color if specified
        if 'color' in self.attributes:
            content = tex_cmd(cmd='textcolor',
                              attributes=self.attributes['color'],
                              formatted_content=content)
        if 'bold' in self.attributes or self.name == 'termb':
            content = tex_cmd(cmd='boldsymbol', formatted_content=content)

        # Remove extra space around the content
        content = content.strip()

        if mathmode:
            return content
        else:
            if self.block_equation or self.paragraph_role == 'block':
                return tex_env(env=self.tex_env, attributes=self.attributes,
                               formatted_content=content, min_newlines=True)
            else:
                return tex_cmd(cmd='ensuremath', attributes=self.attributes,
                               formatted_content=content)
