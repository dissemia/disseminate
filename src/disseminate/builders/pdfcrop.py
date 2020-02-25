"""
A builder to crop pdf files
"""
from .builder import Builder
from .validators import validate_tuple


class PdfCrop(Builder):
    """A builder to crop a pdf and form a cropped pdf.

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

    action = "pdf-crop-margins -o {outfilepath} {infilepaths}"
    priority = 1000
    required_execs = ('pdf-crop-margins',)

    infilepath_ext = '.pdf'
    outfilepath_ext = 'pdf'
    outfilepath_append = '_crop'

    crop_percentage = None

    def __init__(self, env, *args, **kwargs):
        for item in ('crop', 'crop_percentage'):
            if item in kwargs:
                crop = kwargs.pop(item)
                crop = (validate_tuple(crop, type=int, length=4,
                                       raise_error=True)
                        if not isinstance(crop, int) else crop)
                self.crop_percentage = crop

        super().__init__(env, *args, **kwargs)

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.crop_percentage, int):
            args = [args[0]] + ["-p", str(self.crop_percentage)] + args[1:]
        elif isinstance(self.crop_percentage, tuple):
            args = ([args[0]] +
                     ["-p4", *[str(i) for i in self.crop_percentage]] +
                     args[1:])
        return tuple(args)
