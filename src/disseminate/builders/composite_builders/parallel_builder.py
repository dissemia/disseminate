from .composite_builder import CompositeBuilder
from ...paths import TargetPath
from ...paths.utils import find_file


class ParallelBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in parallell (i.e. run the
    subbuilders together at the same time)"""
    parallel = True

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

    def add_build(self, infilepaths=None, outfilepath=None, target=None,
                  context=None, builder_cls=None, **kwargs):
        # Setup the arguments
        context = context or self.env.context

        infilepaths = infilepaths or []
        infilepaths = (infilepaths if isinstance(infilepaths, list) or
                       isinstance(infilepaths, tuple) else [infilepaths])
        infilepaths = [find_file(i, context, raise_error=False) or i
                       for i in infilepaths]

        target = target or self.target

        # Find the builder class
        if builder_cls is None:
            # Get the input extensions for the builder in_ext
            in_exts = [infilepath for infilepath in infilepaths
                       if isinstance(infilepath, str) and
                       infilepath.startswith('.')]
            in_exts += [infilepath.suffix for infilepath in infilepaths
                        if hasattr(infilepath, 'suffix')]

            in_ext = in_exts[0] if in_exts else None

            # Get the output extension for the builder out_ext
            if isinstance(outfilepath, str) and outfilepath.startswith('.'):
                out_ext = outfilepath
            elif hasattr(outfilepath, 'suffix'):
                out_ext = outfilepath.suffix
            else:
                out_ext = None

            builder_cls = self.find_builder_cls(in_ext=in_ext, out_ext=out_ext,
                                                target=target)

        # Create the builder
        builder = builder_cls(env=self.env, infilepaths=infilepaths,
                              outfilepath=outfilepath, context=context,
                              target=target, **kwargs)
        self.subbuilders.append(builder)

        return builder
