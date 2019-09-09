"""
Tags to render equations
"""
from copy import copy

from .img import RenderedImg
from .exceptions import TagError
from .utils import content_to_str
from ..formats import tex_cmd, tex_env
from ..attributes import Attributes


class Eq(RenderedImg):
    """The inline equation tag

    Render an equation in native LaTeX (.tex targets) or into a rendered
    SVG image using LaTeX (.html targets).

    Attributes
    ----------
    aliases : Tuple[str]
        A list of strs for other names a tag goes by
    active : bool
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

    tex_content = None

    default_block_env = "align*"

    def __init__(self, name, content, attributes, context,
                 block_equation=False):
        assert (context.is_valid('renderers') and
                'equation' in context['renderers'])
        self.block_equation = block_equation

        # Ensure the attributes argument is an Attributes type
        attributes = Attributes(attributes)

        # Get various properties from the attributes
        env = attributes.get('env', target='.tex')
        self.block_equation = (True if env is not None or
                               block_equation else False)
        self.tex_env = env if env is not None else self.default_block_env

        # Prepare the tag to only have its contents processed
        self.context = context
        self.content = content
        self.attributes = attributes

        # Replace macros and process content
        self.process(names='process_content')

        # Take the content, and convert it to latex. Save the tex_content
        # separately because the contents of this tag will be converted to
        # an image path by the parent class.
        tex_content = content_to_str(self.content, target='.tex', mathmode=True)
        tex_content = tex_content.strip(' \t\n')
        self.tex_content = tex_content
        content = self.tex

        # Crop equation images created by the dependency manager. This removes
        # white space around the image so that the equation images.
        # Note: This crop command should not cut off baselines such that
        # equation images won't line up properly with the surrounding text.
        # ex: H vs Hy
        attributes['crop'] = (100, 100, 0, 0)

        super().__init__(name=name, content=content, attributes=attributes,
                         context=context, render_target='.tex')

    def render_content(self, content, context):
        """Render the content in LaTeX into a valid .tex file."""
        # Get the renderer for the equation
        if ('renderers' not in context or
           'equation' not in context['renderers']):
            raise TagError("Missing equation renderer in the document context")
        renderer = context['renderers']['equation']

        # Make a copy of the context and add the content as the 'body' entry.
        context_cp = copy(context)
        context_cp['body'] = content

        # Get the kwargs and args to pass to the template
        kwargs = self.template_kwargs()

        return renderer.render(context=context_cp, target='.tex', **kwargs)

    def html_fmt(self, content=None, attributes=None, level=1):
        attrs = attributes if attributes is not None else self.attributes.copy()

        if self.block_equation:
            attrs['class'] = 'eq blockeq'
        else:
            attrs['class'] = 'eq'
        return super(Eq, self).html_fmt(content=content, attributes=attrs,
                                        level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        if content is None:
            content = (self.tex_content if self.tex_content is not None
                       else self.content)

        # Add bold and color if specified
        attributes = attributes if attributes is not None else self.attributes
        if 'color' in attributes:
            content = tex_cmd(cmd='textcolor',
                              attributes=attributes['color'],
                              formatted_content=content)
        if 'bold' in attributes or self.name == 'termb':
            content = tex_cmd(cmd='boldsymbol', formatted_content=content)

        # Remove extra space around the content
        content = content.strip()

        if mathmode:
            return content
        else:
            if self.block_equation or self.paragraph_role == 'block':
                return tex_env(env=self.tex_env, attributes=attributes,
                               formatted_content=content, min_newlines=True)
            else:
                return tex_cmd(cmd='ensuremath', attributes=attributes,
                               formatted_content=content)
