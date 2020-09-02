"""
Receivers to tie builders to other events
"""
from .builder import Builder
from .composite_builders import ParallelBuilder
from .exceptions import BuildError
from ..signals import signal


document_onload = signal('document_onload')
document_build = signal('document_build')
document_build_needed = signal('document_build_needed')

# Loaded after headers but before tags
@document_onload.connect_via(order=2000)
def add_target_builders(document, context):
    """Add target builders to a document context"""
    builders = context.setdefault('builders', dict())
    builders.clear()  # Reset builders if the targets for the doc have changed

    environment = context['environment']
    for target in context.targets:
        target = target if target.startswith('.') else '.' + target

        if target not in builders:
            builder_cls = Builder.find_builder_cls(in_ext='.dm', out_ext=target)
            builders[target] = builder_cls(env=environment, context=context)


# Loaded on document build
@document_build.connect_via(order=1000)
def build(document, complete=True):
    """Build a document tree's targets (and subdocuments) using the target
    builders."""

    # Setup a parallel builder
    context = document.context
    env = context['environment']
    root_builder = env.create_root_builder(document)

    if complete:
        while root_builder.status in {'building', 'ready'}:
            root_builder.build(complete=False)
    else:
        if root_builder.status in {'building', 'ready'}:
            root_builder.build(complete=False)

    return root_builder.status


@document_build_needed.connect_via(order=1000)
def build_needed(document):
    """Evaluate whether any of the target builders need to be build"""

    # Get the target builders
    # The builders dict should be in context from add_target_builders
    context = document.context

    assert 'builders' in context
    builders = context['builders']

    # check if any of the target builders need building
    return any(b.build_needed() for b in builders.values())
