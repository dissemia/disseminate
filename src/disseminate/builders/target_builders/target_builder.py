"""
A builder for document targets.
"""
import logging

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
    parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
    outfilepath : Optional[:obj:`pathlib.Path`]
        If specified, the path for the output file.
    subbuilders : List[:obj:`.builders.Builder`]
        A list of subbuilders to add to this TargetBuilder.

    Attributes
    ----------
    only_root : Optional[bool]
        If True, only add the target builder for the root document.
    add_parallel_builder : Optional[bool]
        If True (default), create a parallel builder for adding dependencies
        for a target.
    add_render_builder : Optional[bool]
        If True (default), create a render builder to render the target.
    """

    active_requirements = ('priority',)
    priority = 1000
    context = weakattr()

    use_media = False
    use_cache = False
    chain_on_creation = False
    copy = False
    clear_done = False

    only_root = False
    add_parallel_builder = True
    add_render_builder = True

    parameters_from_signals = 'ref_label_dependencies'

    _parallel_builder = None
    _render_builder = None

    def __init__(self, env, context, parameters=None, outfilepath=None,
                 subbuilders=None, use_cache=None, **kwargs):
        if __debug__ and 'src_filepath' in context:
            # log the creation of the target builder
            msg = "Add target builder '{}' to document '{}'"
            logging.debug(msg.format(self.__class__.__name__,
                                     context['src_filepath']))

        # Configure the parameters
        self.context = context
        parameters = parameters if parameters is not None else []
        parameters = (list(parameters) if isinstance(parameters, tuple) or
                      isinstance(parameters, list) else [parameters])
        subbuilders = subbuilders or []

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

        # Setup parameters specific to this target builder.
        # Make sure the src_filepath is in the parameters, since if this
        # changes, it changes the input parameter hash for the decider
        if len(parameters) == 0 and 'src_filepath' in context:
            parameters.append(context['src_filepath'])

        # Make sure the name of the builder is included in the parameters,
        # since this will change the build hash for different target builders
        parameters.insert(0, "build '{}'".format(self.__class__.__name__))

        # Determine if this target builder matches a document target
        is_document_target = self.outfilepath_ext in context.targets

        # Only use cache for outfilepaths if this is not a document target
        if use_cache is None:
            use_cache = False if is_document_target else True

        # Setup the outfilepath, if one isn't specified.
        if outfilepath is None:
            outfilepath = generate_outfilepath(env=env,
                                               parameters=parameters,
                                               target=self.outfilepath_ext,
                                               ext=self.outfilepath_ext,
                                               use_cache=use_cache,
                                               use_media=self.use_media)

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
            # Add ref label dependencies
            render_builder.parameters_from_signals = 'ref_label_dependencies'

            subbuilders.append(render_builder)
            self._render_builder = render_builder

        # Initialize builder
        super().__init__(env, parameters=parameters, outfilepath=outfilepath,
                         subbuilders=subbuilders, use_cache=use_cache,
                         **kwargs)

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
