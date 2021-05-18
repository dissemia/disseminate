"""
A builder to scale svg
"""
from .builder import Builder


class ScaleSvg(Builder):
    """A builder to scale svgs.

    Parameters
    ----------
    parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
        This tuple should have the 'scale' tuple value specified, which is the
        scale to increase or decrease the image.
        ex: ('scale', 2.0) will double the image size.
    env: :obj:`.builders.Environment`
        The build environment
    """

    action = ("rsvg-convert -f svg -o {builder.outfilepath} "
              "{builder.infilepaths}")
    available = False  # Used as part of sequential builders
    priority = 1000
    required_execs = ('rsvg-convert',)

    infilepath_ext = '.svg'
    outfilepath_ext = '.svg'
    outfilepath_append = '_scale'

    scale = None

    def __init__(self, env, **kwargs):
        super().__init__(env, **kwargs)

        # Set the scale of the svg image
        scale = self.get_parameter('scale')
        try:
            self.scale = float(scale)
        except (ValueError, TypeError):
            msg = ("A scale parameter (float) should be specified for the "
                   "'{}' Builder")
            raise ValueError(msg.format(self.__class__.__name__))

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        args = [args[0]] + ["-z", str(self.scale)] + args[1:]
        return tuple(args)
