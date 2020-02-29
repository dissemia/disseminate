from ..builder import Builder
from ..copy import Copy
from ..exceptions import BuildError
from ...utils.classes import all_subclasses
from ... import settings


class CompositeBuilder(Builder):
    """A builder that integrates multiple (sub)-builders
     Notes
    -----
    - The build filepaths for subbuilders are set as follows, with user-supplied
      paths in parentheses:
      - builder - subbuilder1 (infilepaths) - outfilepath1
                - subbuilder2 outfilepath2 - outfilepath3
                - subbuilder3 outfilepath3 - outfilepath4
                - outfilepath4 - (outfilepath)
    """
    subbuilders = None

    active_requirements = ('priority',)
    parallel = False

    _available_builders = None

    def run_cmd_args(self):
        """Format the for all sub commands

        Returns
        -------
        run_cmd_args : Tuple[str]
            A tuple of the arguments for all sub-builders
        """
        args = []
        for subbuilder in self.subbuilders:
            args += list(subbuilder.run_cmd_args())
        return tuple(args)

    def build(self, complete=False):
        def run_build(self):
            status = 'done'
            for builder in self.subbuilders:
                if builder.status == 'building':
                    status = 'building'
                    if self.parallel:
                        continue
                    else:
                        break
                elif builder.status == 'ready':
                    builder.build()
                    status = 'building'
                    if self.parallel:
                        continue
                    else:
                        break
                elif builder.status == 'done':
                    status = "done"
            return status

        if complete:
            while self.status in {'building', 'ready'}:
                run_build(self)
        else:
            if self.status in {'building', 'ready'}:
                run_build(self)

        return self.status

    @classmethod
    def find_builder_cls(cls, document_target, infilepath, outfilepath=None):
        """Return a builder class"""
        assert document_target in settings.tracked_deps
        tracked_deps = settings.tracked_deps[document_target]

        # Cache the available builders
        if cls._available_builders is None:
            subclses = dict()
            for builder in all_subclasses(Builder):
                if getattr(builder, 'available', False):
                    continue

                key = (builder.infilepath_ext, builder.outfilepath_ext)
                subclses[key] = builder
            cls._available_builders = subclses

        # Otherwise see if there's a valid outfilepath
        infilepath_suffix = infilepath.suffix
        outfilepath_suffix = outfilepath.suffix if outfilepath else None
        if outfilepath_suffix:
            key = (infilepath_suffix, outfilepath_suffix)
            if key in cls._available_builders:
                return cls._available_builders[key]
        else:
            # Otherwise see if there's a builder we can use
            for dep in tracked_deps:
                key = (infilepath_suffix, dep)
                if key in cls._available_builders:
                    return cls._available_builders[key]

        # if the infilepath is a tracked dependency, then just use a
        # copy builder
        if infilepath_suffix in tracked_deps:
            return Copy

        # No builder could be found
        msg = ("A builder cannot be found for '{}'. Available formats "
               "are: {}".format(infilepath, tracked_deps))
        raise BuildError(msg)

    def add_build(self, document_target, infilepaths, outfilepath=None,
                  context=None, **kwargs):
        """Create and add a sub-builder to the composite builder.

        Parameters
        ----------
        document_target : str
            Find a builder that can build and convert the file
            to a format needed by the document_target. ex: '.html', '.pdf'
        infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
            The filepaths for input files in the build
        outfilepath : Optional[:obj:`.paths.TargetPath`]
            If specified, the path for the output file.
        context : Optional[:obj:`.document_context.DocumentContext`]
            If specified, use the given path to find
        """
        # Setup the parameters
        infilepaths = ([infilepaths] if
                       not isinstance(infilepaths, list) and
                       not isinstance(infilepaths, tuple) else
                       infilepaths)

        # Find correct builder from the infilepath extension and, possible, the
        # outfilepath extension
        infilepath_ext = infilepaths[0].suffix