"""
Equation tags.
"""
from .img import RenderedImg
from ..attributes import set_attribute
from . import settings


class Eq(RenderedImg):
    """The inline equation tag"""

    src_filepath = None
    active = True

    def __init__(self, name, content, attributes,
                 local_context, global_context):
        # Save the content for the tex output
        self._tex_content = content

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
                                 template='eq')

    def tex(self, level=1):
        return "$" + ''.join(self._tex_content) + "$"
