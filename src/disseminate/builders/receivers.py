"""
Receivers to tie builders to other events
"""
from ..signals import signal
from .builder import Builder

document_onload = signal('document_onload')

# Loaded after headers but before tags
@document_onload.connect_via(order=2000)
def add_target_builders(document, context):
    """Add target builders to a document context"""
    builders = context.setdefault('builders', dict())
    builders.clear()  # Reset builders if the targets for the doc have changed

    environment = context['environment']
    for target in context['targets']:
        target = target if target.startswith('.') else '.' + target
        if target not in builders:
            builder_cls = Builder.find_builder_cls(in_ext='.dm', out_ext=target)
            builders[target] = builder_cls(env=environment, context=context)
