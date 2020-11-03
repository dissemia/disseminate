"""
A builder to crop pdf files
"""
from .builder import Builder
from .validators import validate_tuple


class PdfCrop(Builder):
    """A builder to crop a pdf and form a cropped pdf.

    Parameters
    ----------
    parameters : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
        This tuple may have the 'crop' tuple value or 'crop_percentage' value
        specified. If specified the borders by the given single percentage
        or the 4 percentages for the left, bottom, right, and top margins.
        ex: ('crop', 10) or ('crop', (10, 20, 10,20) or ('crop_percentage', 10)
    """

    action = "pdf-crop-margins -o {builder.outfilepath} {builder.infilepaths}"
    available = False  # Use as part of sequential builders
    priority = 1000
    required_execs = ('pdf-crop-margins',)

    infilepath_ext = '.pdf'
    outfilepath_ext = 'pdf'
    outfilepath_append = '_crop'

    crop_percentage = None
    offset = None

    def __init__(self, env, **kwargs):

        super().__init__(env, **kwargs)

        # Set the crop for the image
        crop = (self.get_parameter('crop') or
                self.get_parameter('crop_percentage'))
        if crop:
            # Validate the crop arguments, if specified
            crop = (validate_tuple(crop, type=int, length=4,
                                   raise_error=True)
                    if not isinstance(crop, int) else crop)
            self.crop_percentage = crop

        # Set the offset for the image
        offset = self.get_parameter('offset')
        if offset:
            # Validate the crop arguments, if specified
            offset = (validate_tuple(offset, type=int, length=4,
                                     raise_error=True)
                      if not isinstance(offset, int) else offset)
            self.offset = offset

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        # Add crop percentage options
        if isinstance(self.crop_percentage, int):
            args = [args[0]] + ["-p", str(self.crop_percentage)] + args[1:]
        elif isinstance(self.crop_percentage, tuple):
            args = ([args[0]] +
                    ["-p4", *[str(i) for i in self.crop_percentage]] +
                    args[1:])

        # Add crop offsets
        if isinstance(self.offset, tuple):
            args = ([args[0]] +
                    ["-a4", *[str(i) for i in self.offset]] +
                    args[1:])
        return tuple(args)
