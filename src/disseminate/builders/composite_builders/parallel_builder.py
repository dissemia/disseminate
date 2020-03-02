from .composite_builder import CompositeBuilder
from ..builder import Builder
from ..copy import Copy
from ..exceptions import BuildError
from ...paths.utils import search_paths
from ...utils.classes import all_subclasses
from ... import settings


class ParallelBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in parallell (i.e. run the
    subbuilders together at the same time)"""
    parallel = True

    _available_builders = None

    @property
    def status(self):
        statuses = {sb.status for sb in self.subbuilders}
        if 'inactive' in statuses:
            return 'inactive'
        elif 'missing' in statuses:
            return 'missing'
        elif 'building' in statuses:
            return 'building'
        elif {'done'} == statuses:  # all subbuilders are done
            return 'done'
        return 'ready'

    @classmethod
    def find_builder_cls(cls, document_target, infilepath, outfilepath=None):
        """Return a builder class"""
        assert document_target in settings.tracked_deps
        tracked_deps = settings.tracked_deps[document_target]

        # Cache the available builders
        if cls._available_builders is None:
            subclses = dict()

            for builder in all_subclasses(Builder):
                if not getattr(builder, 'available', False):
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

        # Find the infilepath files
        context = context or self.env.context
        infilepaths = [search_paths(i, context) for i in infilepaths]

        # Find correct builder class to use
        builder_cls = self.find_builder_cls(document_target=document_target,
                                            infilepath=infilepaths[0],
                                            outfilepath=outfilepath)

        # Create the subbuilder and add it to the list of subbuilders
        builder = builder_cls(self.env, infilepaths=infilepaths,
                              outfilepath=outfilepath, **kwargs)
        self.subbuilders.append(builder)
        return builder