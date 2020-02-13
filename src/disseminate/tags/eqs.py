"""
Tags to render equations
"""
from copy import copy

from .tag import TagFactory
from .img import RenderedImg
from .exceptions import TagError
from .receivers import process_content, process_macros
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
    input_format = '.tex'

    process_content = False

    block_equation = None
    bold = None
    color = None

    tex_content = None
    tex_paragraph_newlines = False

    default_block_env = "align*"

    def __init__(self, name, content, attributes, context,
                 block_equation=False):
        self.block_equation = block_equation

        # Convert the content into a string
        content = content_to_str(content, target='.tex',
                                 mathmode=True)
        content = content.strip(' \t\n')

        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)
        #
        # # Get various properties from the attributes
        # env = attributes.get('env', target='.tex')
        # self.block_equation = (True if env is not None orself.block_equation else False)
        # self.tex_env = env if env is not None else self.default_block_env

    def prepare_content(self, content=None, context=None):
        """Render the content in LaTeX into a valid .tex file."""
        # Get the renderer for the equation
        if ('renderers' not in context or
           'equation' not in context['renderers']):
            raise TagError("Missing equation renderer in the document context")
        renderer = context['renderers']['equation']

        # Get the unspecified arguments
        content = content if content is not None else self.tex
        context = context if context is not None else context

        # Make a copy of the context and add the content as the 'body' entry.
        context_cp = copy(context)
        context_cp['body'] = content
        kwargs = dict()

        return renderer.render(context=context_cp, target='.tex', **kwargs)

    def html_fmt(self, content=None, attributes=None, level=1):
        attrs = attributes if attributes is not None else self.attributes.copy()

        # Crop equation images created by the dependency manager. This removes
        # white space around the image so that the equation images.
        # Note: This crop command should not cut off baselines such that
        # equation images won't line up properly with the surrounding text.
        # ex: H vs Hy
        attrs['crop'] = (100, 100, 0, 0)

        if self.block_equation:
            attrs['class'] = 'eq blockeq'
        else:
            attrs['class'] = 'eq'
        return super(Eq, self).html_fmt(content=content, attributes=attrs,
                                        level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Retrieve unspecified arguments
        attributes = attributes if attributes is not None else self.attributes
        content = content if content is not None else self.content

        # Determine the environment
        env = attributes.get('env', target='.tex') or self.default_block_env
        block_equation = self.block_equation or self.paragraph_role == 'block'

        # Add bold and color if specified
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
            if block_equation:
                return tex_env(env=env, attributes=attributes,
                               formatted_content=content, min_newlines=True)
            else:
                return tex_cmd(cmd='ensuremath', attributes=attributes,
                               formatted_content=content)
