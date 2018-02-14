"""
Asymptote tags
"""
from .img import RenderedImg


class Asy(RenderedImg):
    """The asy tag for inserting asymptote images."""

    src_filepath = None
    manage_dependencies = True
    active = True

    def __init__(self, name, content, attributes,
                 local_context, global_context):
        super(Asy, self).__init__(name=name, content=content,
                                  attributes=attributes,
                                  local_context=local_context,
                                  global_context=global_context,
                                  render_target='.asy')
