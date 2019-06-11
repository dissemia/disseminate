"""
Utility functions for renderers.
"""
from .base_renderer import BaseRenderer

def load_renderers(context):
    """Load the renderers in the context.

    Parameters
    ----------
    context : :obj:`DocumentContext <.DocumentContext>`
        The context for the document requiring renderers.
    """

    # Create 'renderers' dict with 'template', 'eq' entries.
    renderers = context.setdefault('renderers', dict())

    # Get the subclasses of the BaseRenderer
    renderer_clses = sorted(BaseRenderer.__subclasses__(),
                            key=lambda r: r.order)
    renderer_cls = renderer_clses[0]

    # Create the template renderer, if needed.
    template = context.get('template', 'default/template')
    if ('template' not in renderers or
       renderers['template'].template != template):
        template_renderer = renderer_cls(context=context,
                                         template=template)
        renderers['template'] = template_renderer

    # Create the equation renderer, if needed.
    if 'equation' not in renderers:
        equation_template = context.get('equation_template', 'default/eq')
        equation_renderer = renderer_cls(context=context,
                                         template=equation_template)
        renderers['equation'] = equation_renderer

    # Add the renderer paths. When creating renderers, paths are added to the
    # context['paths'] entry. However, if these renderers are not created
    # (because they already exist), this function still adds the renderer's
    # paths to the context['paths'], which may have been reset.
    add_context_paths(renderers=renderers.values(), context=context)

    return renderers


def add_context_paths(renderers, context):
    """Add paths from renderers to the context's 'paths' entry.

    Parameters
    ----------
    renderers : List[:obj:`Type[BaseRenderer] <.renderers.BaseRenderer>`]
        The renderers for a document.
    context : :obj:`DocumentContext <.context.DocumentContext>`
        The context for the document.
    """
    for renderer in renderers:
        renderer.add_context_paths(context=context)
