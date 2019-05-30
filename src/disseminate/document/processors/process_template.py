"""
Processor for templates in document contexts.
"""
from .process_context import ProcessContext
from ...renderers import BaseRenderer


class ProcessContextTemplate(ProcessContext):
    """Process the template entries in a given context."""

    order = 300

    def __call__(self, context):
        # Get the subclasses of the BaseRenderer
        renderer_clses = BaseRenderer.renderer_subclasses()
        renderer_cls = renderer_clses[0]

        # Create the template renderer.
        template = context.get('template', 'default/template')
        template_renderer = renderer_cls(context=context,
                                         template=template,
                                         targets=context.targets,
                                         module_only=False)
        context['template_renderer'] = template_renderer

        # Create the equation renderer.
        equation_template = context.get('equation_template', 'default/eq')
        equation_renderer = renderer_cls(context=context,
                                         template=equation_template,
                                         targets=['.tex'],
                                         module_only=False)
        context['equation_renderer'] = equation_renderer
