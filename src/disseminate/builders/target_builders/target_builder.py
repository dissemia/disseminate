"""
A builder for document targets.
"""
from ..jinja_render import JinjaRender
from ..composite_builders import SequentialBuilder, ParallelBuilder
from ..utils import generate_outfilepath
from ...utils.classes import weakattr


class TargetBuilder(SequentialBuilder):
    """A builder for a document target, like html, tex or pdf

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    context: :obj:`.context.Context`
        The context dict for the document being rendered.
    iparameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
    outfilepath : Optional[:obj:`pathlib.Path`]
        If specified, the path for the output file.
    subbuilders : List[:obj:`.builders.Builder`]
        A list of subbuilders to add to this TargetBuilder.

    Attributes
    ----------
    add_parallel_builder : Optional[bool]
        If True (default), create a parallel builder for adding dependencies for
        a target.
    add_render_builder : Optional[bool]
        If True (default), create a render builder to render the target.
    """

    active_requirements = ('priority',)
    context = weakattr()

    use_media = False
    use_cache = False
    chain_on_creation = False
    copy = False
    clear_done = False

    add_parallel_builder = True
    add_render_builder = True

    _parallel_builder = None
    _render_builder = None

    def __init__(self, env, context, parameters=None, outfilepath=None,
                 subbuilders=None, **kwargs):
        # Configure the parameters
        self.context = context

        # Determine the target for the TargetBuilder
        if 'target' in kwargs:
            pass
        elif 'target' not in kwargs and self.target is not None:
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

        if parameters is None and 'src_filepath' in context:
            parameters = context['src_filepath']

        # Determine if this target builder matches a document target
        is_document_target = (document is not None and
                              self.outfilepath_ext in document.targets)

        # Only use cache for outfilepaths if this is not a document target
        use_cache = False if is_document_target else True

        # Setup the outfilepath, if one isn't specified.
        if outfilepath is None:
            if is_document_target:
                # Use the document target as the outfilepath, if this target is
                # listed in the document targets
                outfilepath = document.targets[self.outfilepath_ext]
            else:
                # Otherwise create one from the src_filepath
                outfilepath = generate_outfilepath(env=env,
                                                   parameters=parameters,
                                                   target=self.outfilepath_ext,
                                                   ext=self.outfilepath_ext,
                                                   use_cache=use_cache,
                                                   use_media=self.use_media)
        # Setup the labels

        # Setup the subbuilders
        subbuilders = subbuilders or []

        # Add a parallel builder for dependencies
        if self.add_parallel_builder:
            parallel_builder = ParallelBuilder(env=env, **kwargs)
            subbuilders.append(parallel_builder)
            self._parallel_builder = parallel_builder

        # Add a render builder for the final jinja file
        if self.add_render_builder:
            render_builder = JinjaRender(env, context, outfilepath=outfilepath,
                                         render_ext=self.outfilepath_ext,
                                         **kwargs)
            subbuilders.append(render_builder)
            self._render_builder = render_builder

        # Initialize builder
        super().__init__(env, parameters=parameters, outfilepath=outfilepath,
                         subbuilders=subbuilders, use_cache=use_cache, **kwargs)

    def build_needed(self, reset=False):
        """Determine whether a build is needed."""
        if self.decision is None:
            decider = self.env.decider
            self.decision = decider.decision

        # Get the src_filepath for the document
        inputs = list(self.parameters)

        # Get the (sorted) labels for the document

        return self.decision.build_needed(inputs=inputs,
                                          output=self.outfilepath,
                                          reset=reset)

    @property
    def outfilepath(self):
        if self._render_builder is not None:
            return self._render_builder.outfilepath
        else:
            return SequentialBuilder.outfilepath.fget(self)

    @outfilepath.setter
    def outfilepath(self, value):
        if self._render_builder is not None:
            self._render_builder.outfilepath = value
        else:
            SequentialBuilder.outfilepath.fset(self, value)

    def add_build(self, parameters, outfilepath=None, context=None,
                  use_cache=None, **kwargs):
        """Create and add a sub-builder to the composite builder."""
        use_cache = use_cache or self.use_cache

        par_builder = self._parallel_builder
        builder = par_builder.add_build(parameters=parameters,
                                        outfilepath=outfilepath,
                                        context=context,
                                        use_cache=use_cache,
                                        **kwargs)
        return builder

    def build(self, complete=False):
        # Reload the document
        context = self.context
        document = getattr(context, 'document', None)
        if document is not None:
            document.load()

        # Run the build
        status = super().build(complete=complete)

        return status

    def chain_subbuilders(self):
        return None
