"""
Receivers to tie builders to other events
"""
from .builder import Builder
from .exceptions import BuildError
from ..signals import signal
from .. import settings

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
def build(document):
    """Build a document's targets using the target builders."""
    # Get the target builders
    # The builders dict should be in context from add_target_builders
    context = document.context
    assert 'builders' in context
    builders = context['builders']

    # Go through each document target and run the target build
    statuses = []
    for target in context.targets:
        # target builder should be in builders from add_target_builders
        assert target in builders

        target_builder = builders[target]

        status = target_builder.build(complete=True)
        statuses.append(status)

        if status != 'done':
            msg = ("An error was encountered with builder '{}'. The build "
                   "returned the status '{}'")
            raise BuildError(msg.format(target_builder, status))

    return statuses


@document_build_needed.connect_via(order=1000)
def build_needed(document):
    # Get the target builders
    # The builders dict should be in context from add_target_builders
    context = document.context
    assert 'builders' in context
    builders = context['builders']

    # check if any of the target builders need building
    return any(b.build_needed() for b in builders.values())
