from ..builder import Builder


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

    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)

        # Load the subbuilders
        self.subbuilders = [arg for arg in args if isinstance(arg, Builder)]
        self.subbuilders += list(kwargs.pop('subbuilders', []))

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
