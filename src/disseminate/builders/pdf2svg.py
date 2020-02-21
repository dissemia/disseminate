"""
A builder to convert from PDF to SVG
"""
from .builder import Builder
from .composite_builders import SequentialBuilder
from .pdfcrop import PdfCrop
from .scalesvg import ScaleSvg


class Pdf2svg(Builder):
    """A builder to convert from pdf to svg."""

    action = "pdf2svg {infilepaths} {outfilepath}"
    priority = 1000
    required_execs = ('pdf-crop-margins',)

    infilepath_ext = '.pdf'
    outfilepath_ext = '.svg'

    page_no = None

    def __init__(self, env, *args, **kwargs):
        # Get the page number
        if 'page' in kwargs or 'page_no' in kwargs:
            page_no = (kwargs.pop('page') if 'page' in kwargs else
                       kwargs.pop('page_no'))
            page_no = int(page_no)
            self.page_no = page_no

        # Get parameters related to subbuilders and add these subbuilders
        if 'crop' in kwargs or 'crop_percentage' in kwargs:
            crop = kwargs.pop('crop', None)
            crop = kwargs.pop('crop_percentage', crop)
            pdfcrop = PdfCrop(env=env, crop=crop, *args, **kwargs)
            args += (pdfcrop,)

        if 'scale' in kwargs:
            scale = kwargs.pop('scale')
            scalesvg = ScaleSvg(env=env, scale=scale, *args, **kwargs)
            args += (scalesvg,)

        super().__init__(env, *args, **kwargs)

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.page_no, int):
            args += [self.page_no]
        return tuple(args)


class Pdf2SvgCropScale(SequentialBuilder):
    """Create a CompositeBuilder for Pdf2Svg that includes PdfCrop and ScaleSvg.
    """

    priority = 1000
    infilepath_ext = '.pdf'
    outfilepath_ext = '.svg'

    def __init__(self, env, *args, **kwargs):
        # Create the subbuilders
        if 'crop' in kwargs or 'crop_percentage' in kwargs:
            crop = kwargs.pop('crop', None)
            crop = kwargs.pop('crop_percentage', crop)
            pdfcrop = PdfCrop(env, crop=crop, *args, **kwargs)
            args += (pdfcrop,)

        pdf2svg = Pdf2svg(env, *args, **kwargs)
        args += (pdf2svg,)

        if 'scale' in kwargs:
            scale = kwargs.pop('scale')
            scalesvg = ScaleSvg(env, scale, *args, **kwargs)
            args += (scalesvg,)

        super().__init__(env, *args, **kwargs)
