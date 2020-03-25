"""
A builder for document targets.
"""
from ..jinja_render import JinjaRender
from ..composite_builders import SequentialBuilder, ParallelBuilder
from ..utils import generate_outfilepath
from ...utils.file import mkdir_p
from ...utils.classes import weakattr


class TargetBuilder(SequentialBuilder):
    """A builder for a document target, like html, tex or pdf

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    context: :obj:`.context.Context`
        The context dict for the document being rendered.
    infilepaths, args : Tuple[:obj:`pathlib.Path`]
        The filepaths for input files in the build
    outfilepath : Optional[:obj:`pathlib.Path`]
        If specified, the path for the output file.
    subbuilders : List[:obj:`.builders.Builder`]
        A list of subbuilders to add to this TargetBuilder.
    """

    active_requirements = ('priority',)
    context = weakattr()

    chain_on_creation = False
    copy = False

    _parallel_builder = None
    _render_builder = None

    def __init__(self, env, context, infilepaths=None, outfilepath=None,
                 subbuilders=None, **kwargs):
        # Configure the parameters
        self.context = context

        # Determine the target for the TargetBuilder
        if 'target' not in kwargs and self.target is not None:
            kwargs['target'] = self.target
        elif 'target' not in kwargs and self.outfilepath_ext is not None:
                kwargs['target'] = self.outfilepath_ext
        else:
            msg = ("A target or outfilepath_ext attribute must be specified "
                   "for a TargetBuilder.")
            raise AssertionError(msg)

        # Add the target_builder to the context
        builders = context.setdefault('builders', dict())
        builders[self.outfilepath_ext] = self

        # Setup the paths
        document = getattr(context, 'document', None)
        if infilepaths is None and 'src_filepath' in context:
            infilepaths = context['src_filepath']
        if (outfilepath is None and document is not None and
           self.outfilepath_ext in document.targets):
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
                                     render_ext=self.outfilepath_ext, **kwargs)
        subbuilders.append(render_builder)
        self._render_builder = render_builder

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

    @property
    def outfilepath(self):
        """The output filename and path"""
        # This property is different from the parent by adding the 'target'
        # to the outfilepath
        outfilepath = self._outfilepath

        if outfilepath is None:
            outfilepath = generate_outfilepath(env=self.env,
                                               infilepaths=self.infilepaths,
                                               target=self.target,
                                               append=self.outfilepath_append,
                                               ext=self.outfilepath_ext,
                                               cache=True)

        # Make sure the outfilepath directory exists
        if outfilepath and not outfilepath.parent.is_dir():
            mkdir_p(outfilepath.parent)

        return outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value

    def add_build(self, infilepaths, outfilepath=None,
                  context=None, **kwargs):
        """Create and add a sub-builder to the composite builder."""
        return self._parallel_builder.add_build(infilepaths=infilepaths,
                                                outfilepath=outfilepath,
                                                context=context, **kwargs)

    def build(self, complete=False):
        # Reload the document
        context = self.context
        document = getattr(context, 'document', None)
        if document is not None:
            document.load()

        return super().build(complete=complete)
