from .composite_builder import CompositeBuilder
from ..builder import Builder
from ..copy import Copy
from ..exceptions import BuildError
from ...paths import TargetPath
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
        elif len(statuses) == 0:  # no subbuilders
            return 'done'
        return 'ready'

    def build_needed(self, reset=False):
        return any(sb.build_needed(reset=reset) for sb in self.subbuilders)

    def find_builder_cls(self, infilepath, outfilepath=None):
        """Return a builder class

        Parameters
        ----------
        infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
            The filepaths for input files in the build
        outfilepath : Optional[:obj:`.paths.TargetPath`]
            If specified, the path for the output file.
        """
        assert isinstance(self.target, str), ("A document target must be "
                                              "specified to find the "
                                              "appropriate sub-builder.")
        target = ('.' + self.target if not self.target.startswith('.') else
                  self.target)

        assert target in settings.tracked_deps, ("The document target is not "
                                                 "listed in the "
                                                 "settings.tracked_deps")
        tracked_deps = settings.tracked_deps[target]

        # Retrieve the ParallelBuilder class

        # Cache the available builders
        if ParallelBuilder._available_builders is None:
            subclses = dict()

            for builder in all_subclasses(Builder):
                if not getattr(builder, 'available', False):
                    continue

                key = (builder.infilepath_ext, builder.outfilepath_ext)

                # Only replace an existing builder if it's higher property
                if (key not in subclses or
                   subclses[key].priority < builder.priority):
                    subclses[key] = builder
            ParallelBuilder._available_builders = subclses

        # Otherwise see if there's a valid outfilepath
        infilepath_suffix = infilepath.suffix
        outfilepath_suffix = outfilepath.suffix if outfilepath else None
        if outfilepath_suffix:
            key = (infilepath_suffix, outfilepath_suffix)
            if key in ParallelBuilder._available_builders:
                return ParallelBuilder._available_builders[key]
        else:
            # Otherwise see if there's a builder we can use
            for dep in tracked_deps:
                key = (infilepath_suffix, dep)
                if key in ParallelBuilder._available_builders:
                    return ParallelBuilder._available_builders[key]

        # if the infilepath is a tracked dependency, then just use a
        # copy builder
        if infilepath_suffix in tracked_deps:
            return Copy

        # No builder could be found
        msg = ("A builder cannot be found for '{}'. Available formats "
               "are: {}".format(infilepath, tracked_deps))
        raise BuildError(msg)

    def add_build(self, infilepaths, outfilepath=None,
                  context=None, **kwargs):
        """Create and add a sub-builder to the parallel builder.

        Parameters
        ----------
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
        builder_cls = self.find_builder_cls(infilepath=infilepaths[0],
                                            outfilepath=outfilepath)

        # Create the subbuilder and add it to the list of subbuilders
        builder = builder_cls(self.env, infilepaths=infilepaths,
                              outfilepath=outfilepath, **kwargs)
        self.subbuilders.append(builder)

        # Make sure the target is in the target_root instead of a cache path
        if outfilepath is None:
            target_root = (context['target_root'] if 'target_root' in context
                           else self.env.context['target_root'])
            target = self.target.strip('.')
            outfilepath = builder.outfilepath
            outfilepath = TargetPath(target_root=target_root, target=target,
                                     subpath=outfilepath.subpath)
            builder.outfilepath = outfilepath

            # Reorganize the filepaths if it's a sequential builder
            if hasattr(builder, 'chain_subbuilders'):
                builder.chain_subbuilders()

        return builder
