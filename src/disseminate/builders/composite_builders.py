"""
Composite builders for multiple build commands
"""
from .builder import Builder
from ..utils.file import link_or_copy


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

    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)

        # Load the subbuilders
        self.subbuilders = [arg for arg in args if isinstance(arg, Builder)]
        self.subbuilders += list(kwargs.pop('subbuilders', []))

        # Check that the extensions match
        assert (self.infilepath_ext == self.subbuilders[0].infilepath_ext and
                self.outfilepath_ext == self.subbuilders[-1].outfilepath_ext)

        # Set the infilepaths and outfilepaths
        current_infilepaths = self.infilepaths
        for subbuilder in self.subbuilders:
            # For the subbuilders to work together, reset their infilepaths
            # and outfilepath
            subbuilder.infilepaths = current_infilepaths
            subbuilder.outfilepath = None
            current_infilepaths = [subbuilder.outfilepath]

    @property
    def status(self):
        sb_statuses = {sb.status for sb in self.subbuilders}
        if 'inactive' in sb_statuses:
            return 'inactive'
        elif 'missing' in  sb_statuses:
            return 'missing'
        elif 'building' in sb_statuses:
            return 'building'
        elif {'done'} == sb_statuses:  # all subbuilders are done
            return 'done'
        return 'ready'

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
            status = None
            while status != 'done':
                status = run_build(self)
        else:
            run_build(self)

        if self.status == 'done' and self.subbuilders:
            # Copy the output of the last subbuilder
            link_or_copy(self.subbuilders[-1].outfilepath,
                         self.outfilepath)

        return self.status


class SequentialBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in sequence (i.e. wait for
    one to finish before starting the next)"""
    parallel = False


class ParallelBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in parallell (i.e. run the
    subbuilders together at the same time)"""
    parallel = True
