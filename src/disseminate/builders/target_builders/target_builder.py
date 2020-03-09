"""
A builder for document targets.
"""
from ..builder import Builder
from ..jinja_render import JinjaRender
from ..composite_builders import ParallelBuilder
from ...utils.classes import weakattr


class TargetBuilder(ParallelBuilder):
    """A builder for a document target, like html, tex or pdf"""

    active_requirements = ('priority',)
    target = None

    document = weakattr()

    def __init__(self, env, context, infilepaths=None, outfilepath=None,
                 subbuilders=None, **kwargs):

        target = self.outfilepath_ext.strip('.')
        self.target = target

        # Setup the paths
        document = getattr(context, 'document', None)
        if infilepaths is None and 'src_filepath' in context:
            infilepaths = context['src_filepath']
        if outfilepath is None and document is not None:
            outfilepath = document.targets[self.outfilepath_ext]

        # Setup the labels

        # Setup the subbuilders
        render = JinjaRender(env, context, outfilepath=outfilepath, **kwargs)
        subbuilders = subbuilders or []
        subbuilders.append(render)

        # Initialize builder
        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

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
