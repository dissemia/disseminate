"""
Composite builders for multiple build commands
"""
from .builder import Builder
from .copy import Copy
from .utils import targetpath_to_sourcepath


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
    active_requirements = ('priority',)
    subbuilders = None
    parallel = False

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


class SequentialBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in sequence (i.e. wait for
    one to finish before starting the next)"""
    parallel = False

    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)

        # Load the subbuilders
        self.subbuilders = [arg for arg in args if isinstance(arg, Builder)]
        self.subbuilders += list(kwargs.pop('subbuilders', []))

        # Check that the extensions match
        assert (self.infilepath_ext == self.subbuilders[0].infilepath_ext and
                self.outfilepath_ext == self.subbuilders[-1].outfilepath_ext)

        # Make the last subbuilder a copy builder to copy the result of the
        # sub-builders to the final outfilepath
        self.subbuilders.append(Copy(env))

        # Set the infilepaths and outfilepaths
        current_infilepaths = self.infilepaths
        for subbuilder in self.subbuilders:
            # For the subbuilders to work together, reset their infilepaths
            # and outfilepath
            subbuilder.infilepaths = current_infilepaths
            subbuilder.outfilepath = None

            # Convert the output of subbuilder into an infilepath for the next
            # subbuilder
            infilepath = targetpath_to_sourcepath(subbuilder.outfilepath)
            current_infilepaths = [infilepath]

        # Set the copy builder to point to the final outfilepath
        self.subbuilders[-1].outfilepath = self.outfilepath

    @property
    def status(self):
        if not self.build_needed():
            return 'done'

        # The composite builder's status is basically the same as the next
        # non-done subbuilder. The reason it is implemented this way is to
        # avoid checking the status of intermediary builders whose input files,
        # which may be cached or temporary, may not yet exist.
        number_subbuilders_done = 0
        for subbuilder in self.subbuilders:
            # Bug alert: The subbuilder's status should be retrieved and
            # returned once. Polling the subbuilder.status multiple times may
            # return different answers if the subbuilder changes status when
            # polled at different points.
            status = subbuilder.status
            if status == 'done':
                number_subbuilders_done += 1
            else:
                return status

        if (number_subbuilders_done == len(self.subbuilders) and
           self.outfilepath.exists()):
            self.build_needed(reset=True)
            return 'done'
        else:
            return 'building'


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
        return 'ready'
