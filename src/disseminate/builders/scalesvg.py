"""
A builder to scale svg
"""
from .builder import Builder


class ScaleSvg(Builder):
    """A builder to scale svgs.

    Parameters
    ----------
    infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
        The filepaths for input files in the build
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.
    env: :obj:`.builders.Environment`
        The build environment
    crop_percentage : Optional[int, Tuple[int, int, int, int]]
        If specified crop the borders by the given single percentage or the 4
        percentages for the left, bottom, right, and top margins.
    crop : Optional[int, Tuple[int, int, int, int]]
        Same as 'crop_percentage', but 'crop_percentage' takes precendence.
    """

    action = "rsvg-convert -f svg -o {outfilepath} {infilepaths}"
    priority = 1000
    required_execs = ('rsvg-convert',)

    infilepath_ext = '.svg'
    outfilepath_ext = 'svg'
    outfilepath_append = '_scale'

    scale = None

    def __init__(self, env, scale, *args, **kwargs):
        self.scale = int(scale)

        super().__init__(env=env, *args, **kwargs)

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.scale, int):
            args = [args[0]] + ["-z", str(self.scale)] + args[1:]
        return tuple(args)
