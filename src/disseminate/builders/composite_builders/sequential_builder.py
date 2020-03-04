from .composite_builder import CompositeBuilder
from ..copy import Copy
from ..utils import targetpath_to_sourcepath


class SequentialBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in sequence (i.e. wait for
    one to finish before starting the next)"""
    parallel = False

    def __init__(self, env, **kwargs):
        super().__init__(env, **kwargs)

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
