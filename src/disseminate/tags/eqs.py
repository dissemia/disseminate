"""
Tags to render equations
"""
from .img import Img
from .utils import content_to_str
from ..formats import tex_cmd, tex_env


class Eq(Img):
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
    in_ext = '.render'

    process_content = True

    bold = None
    color = None

    tex_content = None
    tex_paragraph_newlines = False

    default_block_env = "align*"

    _block_equation = False

    def __init__(self, name, content, attributes, context,
                 block_equation=False):
        self.block_equation = block_equation

        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Convert the content into a string formatted for latex
        content = content_to_str(self.content, target='.tex',
                                 mathmode=True)
        self.content = content.strip(' \t\n')

    @property
    def block_equation(self):
        return (self._block_equation or
                'env' in self.attributes or
                self.paragraph_role == 'block')

    @block_equation.setter
    def block_equation(self, value):
        self._block_equation = value

    def html_fmt(self, content=None, attributes=None, context=None, level=1):
        attrs = attributes or self.attributes.copy()

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

        # Create a special context for this tag specifically
        if context is None:
            context = self.context.filter(['paths', 'builders'])
            context['eq'] = self
            context['template'] = 'default/eq'

        return super(Eq, self).html_fmt(content=content, attributes=attrs,
                                        context=context, level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False,
                context=None, level=1):
        # Retrieve unspecified arguments
        attributes = attributes or self.attributes
        content = content or self.content

        # Determine the environment
        env = attributes.get('env', target='.tex') or self.default_block_env

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
            if self.block_equation:
                return tex_env(env=env, attributes=attributes,
                               formatted_content=content, min_newlines=True)
            else:
                return tex_cmd(cmd='ensuremath', attributes=attributes,
                               formatted_content=content)
