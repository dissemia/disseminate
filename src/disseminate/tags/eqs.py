"""
Equation tags.
"""
from .core import Tag
from .img import RenderedImg
from ..attributes import set_attribute
from . import settings


class Eq(RenderedImg):
    """The inline equation tag"""

    aliases = ('term',)
    src_filepath = None
    active = True

    tex_format = "\\ensuremath{{{content}}}"

    def __init__(self, name, content, attributes,
                 local_context, global_context, eq_template=None):
        # Set the equation template for rendering pdf/svg versions of equations
        eq_template = 'eq' if eq_template is None else eq_template

        # Add css class for html formatting
        attributes = set_attribute(attributes, ('class', 'eq'))
        # attributes = set_attribute(attributes,
        #                            ('scale', str(settings.eq_svg_scale)))
        # attributes = set_attribute(attributes,
        #                            ('crop', str(settings.eq_svg_crop)))

        # Save the raw content and format the content in tex
        self._raw_content = content
        content = self.tex()

        super(Eq, self).__init__(name=name, content=content,
                                 attributes=attributes,
                                 local_context=local_context,
                                 global_context=global_context,
                                 render_target='.tex',
                                 template=eq_template)

    def tex(self, level=1, content=None):
        content = self._raw_content
        if isinstance(content, list):
            new_content = [i.tex(level+1) if hasattr(i, 'tex') else
                           self.tex_format.format(content=i)
                           for i in content]
            return ''.join(new_content)
        else:
            return self.tex_format.format(content=content)


class EqBold(Eq):
    """A bolded inline equation."""

    aliases = ('termb',)

    tex_format = "\\ensuremath{{\\boldsymbol{{{content}}}}}"
