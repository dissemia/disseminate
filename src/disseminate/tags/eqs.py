"""
Equation tags.
"""
from .img import RenderedImg
from ..attributes import set_attribute
from . import settings


class Eq(RenderedImg):
    """The inline equation tag"""

    aliases = ('term',)
    src_filepath = None
    active = True

    def __init__(self, name, content, attributes,
                 local_context, global_context, eq_template=None):
        # Save the content for the tex output
        self._tex_content = content

        # Set the equation template for rendering pdf/svg versions of equations
        eq_template = 'eq' if eq_template is None else eq_template

        # Add css class for html formatting
        attributes = set_attribute(attributes, ('class', 'eq'))
        attributes = set_attribute(attributes,
                                   ('scale', str(settings.eq_svg_scale)))
        attributes = set_attribute(attributes,
                                   ('crop', str(settings.eq_svg_crop)))

        super(Eq, self).__init__(name=name, content=content,
                                 attributes=attributes,
                                 local_context=local_context,
                                 global_context=global_context,
                                 render_target='.tex',
                                 template=eq_template)

    def tex(self, level=1):
        return "$" + ''.join(self._tex_content) + "$"


class EqBold(Eq):
    """A bolded inline equation."""

    aliases = ('termb',)

    def __init__(self, *args, **kwargs):
        if 'eq_template' not in kwargs:
            kwargs['eq_template'] = 'eq_bold'
        super(EqBold, self).__init__(*args, **kwargs)

    def tex(self, level=1):
        return "$\\boldmath{" + ''.join(self._tex_content) + "}$"