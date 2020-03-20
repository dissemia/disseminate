"""
A builder for document targets.
"""
from ..jinja_render import JinjaRender
from ..composite_builders import SequentialBuilder, ParallelBuilder
from ...utils.classes import weakattr


class TargetBuilder(SequentialBuilder):
    """A builder for a document target, like html, tex or pdf"""

    active_requirements = ('priority',)
    target = None
    context = weakattr()

    chain_on_creation = False
    copy = False

    _parallel_builder = None
    _render_builder = None

    def __init__(self, env, context, infilepaths=None, outfilepath=None,
                 subbuilders=None, **kwargs):

        target = self.outfilepath_ext.strip('.')
        self.target = target
        self.context = context

        # Add the target_builder to the context
        builders = context.setdefault('builders', dict())
        builders[self.outfilepath_ext] = self

        # Setup the paths
        document = getattr(context, 'document', None)
        if infilepaths is None and 'src_filepath' in context:
            infilepaths = context['src_filepath']
        if outfilepath is None and document is not None:
            outfilepath = document.targets[self.outfilepath_ext]

        # Setup the labels

        # Setup the subbuilders
        subbuilders = subbuilders or []

        # Add a parallel builder for dependencies
        parallel_builder = ParallelBuilder(env=env, **kwargs)
        subbuilders.append(parallel_builder)
        self._parallel_builder = parallel_builder

        # Add a render builder for the final jinja file
        render_builder = JinjaRender(env, context, outfilepath=outfilepath,
                                     **kwargs)
        subbuilders.append(render_builder)
        self._render_builder = render_builder

        # Initialize builder
        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    def add_build(self, document_target, infilepaths, outfilepath=None,
                  context=None, **kwargs):
        """Create and add a sub-builder to the composite builder."""
        return self._parallel_builder.add_build(document_target=document_target,
                                                infilepaths=infilepaths,
                                                outfilepath=outfilepath,
                                                context=context, **kwargs)

    def build_needed(self, reset=False):
        """Determine whether a build is needed."""
        if self.decision is None:
            decider = self.env.decider
            self.decision = decider.decision

        # Get the src_filepath for the document
        inputs = list(self.infilepaths)

        # Get the (sorted) labels for the document

        return self.decision.build_needed(inputs=inputs,
                                          output=self.outfilepath,
                                          reset=reset)

    def build(self, complete=False):
        # Reload the document
        context = self.context
        document = getattr(context, 'document', None)
        if document is not None:
            document.load()

        return super().build(complete=complete)
