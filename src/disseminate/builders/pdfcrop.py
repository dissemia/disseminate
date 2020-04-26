"""
A builder to crop pdf files
"""
from .builder import Builder
from .validators import validate_tuple


class PdfCrop(Builder):
    """A builder to crop a pdf and form a cropped pdf.

    Parameters
    ----------
    parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
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

    action = "pdf-crop-margins -o {builder.outfilepath} {builder.infilepaths}"
    available = False  # Use as part of sequential builders
    priority = 1000
    required_execs = ('pdf-crop-margins',)

    infilepath_ext = '.pdf'
    outfilepath_ext = 'pdf'
    outfilepath_append = '_crop'

    crop_percentage = None

    def __init__(self, env, crop=None, crop_percentage=None, **kwargs):

        # Validate the crop arguments, if specified
        if crop or crop_percentage:
            crop = crop_percentage or crop
            crop = (validate_tuple(crop, type=int, length=4,
                                   raise_error=True)
                    if not isinstance(crop, int) else crop)
            self.crop_percentage = crop
        else:
            self.crop_percentage = None

        super().__init__(env, **kwargs)

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.crop_percentage, int):
            args = [args[0]] + ["-p", str(self.crop_percentage)] + args[1:]
        elif isinstance(self.crop_percentage, tuple):
            args = ([args[0]] +
                     ["-p4", *[str(i) for i in self.crop_percentage]] +
                     args[1:])
        return tuple(args)
