from ..builder import Builder


class CompositeBuilder(Builder):
    """A builder that integrates multiple (sub)-builders

    Parameters
    ----------
    subbuilders : Optional[List[:obj:`.builders.Builder`]
        The subbuilders to run as part of this composite builder.

    Attributes
    ----------
    clear_done : bool
        If True (default), remove 'done' subbuilders during the build.

    Notes
    -----
    - The build filepaths for subbuilders are set as follows, with user-supplied
      paths in parentheses:
      - builder - subbuilder1 (parameters) - outfilepath1
                - subbuilder2 outfilepath2 - outfilepath3
                - subbuilder3 outfilepath3 - outfilepath4
                - outfilepath4 - (outfilepath)
    """
    subbuilders = None

    active_requirements = ('priority',)
    parallel = False
    clear_done = True

    def __init__(self, env, subbuilders=None, **kwargs):
        super().__init__(env, **kwargs)

        # Load the subbuilders
        subbuilders = (list(subbuilders) if isinstance(subbuilders, list) or
                       isinstance(subbuilders, tuple) else [])
        subbuilders = [sb for sb in subbuilders if isinstance(sb, Builder)]
        self.subbuilders = subbuilders

    def __len__(self):
        number_subbuilders = 0
        for subbuilder in self.subbuilders:
            number_subbuilders += 1
            if hasattr(subbuilder, 'subbuilders'):
                number_subbuilders += len(subbuilder.subbuilders)
        return number_subbuilders

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
            for builder in list(self.subbuilders):
                if builder.status == 'done':
                    status = "done"
                    # Remove done builders
                    if self.clear_done:
                        self.subbuilders.remove(builder)

                elif builder.status == 'building':
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
                        
                else:
                    return builder.status

            return status

        if complete:
            while self.status in {'building', 'ready'}:
                run_build(self)
        else:
            if self.status in {'building', 'ready'}:
                run_build(self)

        return self.status
