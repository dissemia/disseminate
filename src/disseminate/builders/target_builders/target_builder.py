"""
A builder for document targets.
"""
from ..builder import Builder
from ..jinja_render import JinjaRender
from ..composite_builders import ParallelBuilder
from ...utils.classes import weakattr
from ...paths import TargetPath


class TargetBuilder(ParallelBuilder):
    """A builder for a document target, like html, tex or pdf"""

    active_requirements = ('priority',)

    document = weakattr()
    render_builder = None
    dependencies_builder = None

    def __init__(self, env, document, target, subbuilders=None, **kwargs):
        assert target in document.targets

        # Setup the paths
        outfilepath = document.targets[target]
        context = document.context
        infilepaths = document.src_filepath

        # Setup the labels

        # Setup the subbuilders
        render = JinjaRender(env, context, outfilepath=outfilepath, **kwargs)
        subbuilders = subbuilders or []
        subbuilders.append(render)

        # Initialize builder
        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    def add_build(self, document_target, infilepaths, outfilepath=None,
                  context=None, **kwargs):
        """Add a build to the dependencies builder"""
        self.dependencies_builder.add_build(document_target=document_target,
                                            infilepaths=infilepaths,
                                            outfilepath=outfilepath,
                                            context=context,
                                            front=True,
                                            **kwargs)

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
