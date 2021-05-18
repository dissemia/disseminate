"""
Tags to render equations
"""
from .img import Img
from .utils import content_to_str
from ..formats import tex_cmd, tex_env


class Eq(Img):
    r"""The inline equation tag

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

    #: Holds a dict of sub-context dicts to be used in rendering the equation
    #: to a file. This tag owns these sub-contexts.
    _target_context = None

    def __init__(self, *args, block_equation=False, **kwargs):
        self.block_equation = block_equation
        self._target_context = dict()

        super().__init__(*args, **kwargs)

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

    def tex_fmt(self, content=None, attributes=None, mathmode=False,
                **kwargs):
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

    def html_fmt(self, attributes=None, context=None, method='html',
                 **kwargs):
        # Create a context for the render. This context is owned by this
        # tag
        attrs = attributes or self.attributes.copy()

        # Crop equation images build. This removes white space around the
        # image so that the equation images. Note: This crop command should
        # not cut off baselines such that equation images won't line up
        # properly with the surrounding text. # ex: H vs Hy
        attrs['crop'] = (100, 100, 0, 0)
        attrs['offset'] = (0, 0, -1, 0)

        if self.block_equation:
            attrs['class'] = 'eq blockeq'
        else:
            attrs['class'] = 'eq'

        if context is None and method not in self._target_context:
            # Create a special context for this tag specifically. This tag
            # will own this context
            context = self.context.filter(['paths', 'builders'])
            context['eq'] = self
            context['template'] = 'default/tex/eq'
            self._target_context[method] = context

        context = context or self._target_context[method]
        return super(Eq, self).html_fmt(attributes=attrs, context=context,
                                        method=method, **kwargs)
