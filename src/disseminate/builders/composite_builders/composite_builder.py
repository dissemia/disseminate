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
        def run_build_once(self):
            """Execute one round of the subbuilders"""
            status = 'done'

            for builder in self.subbuilders:
                status = builder.status

                if status == 'done':
                    # The builder is responsible for resetting its build_needed
                    # method after the build is done.
                    continue

                elif status == 'building':
                    if self.parallel:
                        continue
                    else:
                        break

                elif status == 'ready':
                    builder.build()
                    status = 'building'
                    if self.parallel:
                        continue
                    else:
                        break
                        
                else:
                    return status

            return status

        if complete:
            while self.status in {'building', 'ready'}:
                run_build_once(self)
        else:
            if self.status in {'building', 'ready'}:
                run_build_once(self)

        # Get the current status and reset build_needed states
        status = self.status
        if status == 'done':
            self.build_needed(reset=True)

        # Remove finished builders, if specified by 'clear_done'
        if self.clear_done:
            for subbuilder in list(self.subbuilders):
                if subbuilder.status == 'done':
                    self.subbuilders.remove(subbuilder)

        return status

    def print(self, level=1):
        """Print the builder and subbuilders"""
        def print_builder(b, level, num_spaces=2):
            msg = "  " * num_spaces * level
            msg += str(b)  # the __repr__ of the builder
            msg += "({}) ".format(self.outfilepath.subpath)

            # Get builder attributes that are useful to print out
            attrs = ["{}={}".format(attr, getattr(b, attr, None))
                     for attr in ('use_cache', 'use_media', 'clear_done',
                                  'target')
                     if getattr(b, attr, None) is not None]

            if attrs:
                msg += ": " + ", ".join(attrs)
            print(msg)

        print_builder(self, level=level - 1)
        for subbuilder in self.subbuilders:
            if isinstance(subbuilder, CompositeBuilder):
                subbuilder.print(level=level + 1)
            else:
                print_builder(subbuilder, level=level)
