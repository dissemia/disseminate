"""
A builder to convert from PDF to SVG
"""
from .builder import Builder
from .composite_builders import SequentialBuilder
from .pdfcrop import PdfCrop
from .scalesvg import ScaleSvg


class Pdf2svg(Builder):
    """A builder to convert from pdf to svg."""

    action = "pdf2svg {builder.infilepaths} {builder.outfilepath}"
    available = False
    priority = 1000
    required_execs = ('pdf2svg',)

    infilepath_ext = '.pdf'
    outfilepath_ext = '.svg'

    page_no = None

    def __init__(self, env, page=None, page_no=None, **kwargs):
        # Get the page number
        if page or page_no:
            page_no = page or page_no
            page_no = int(page_no)
            self.page_no = page_no

        super().__init__(env, **kwargs)

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.page_no, int):
            args += [self.page_no]
        return tuple(args)


class Pdf2SvgCropScale(SequentialBuilder):
    """Create a CompositeBuilder for Pdf2Svg that includes PdfCrop and ScaleSvg.
    """

    available = True
    priority = 1000
    infilepath_ext = '.pdf'
    outfilepath_ext = '.svg'

    def __init__(self, env, crop=None, crop_percentage=None, scale=None,
                 subbuilders=None, **kwargs):
        # Setup parameters
        subbuilders = (list(subbuilders) if isinstance(subbuilders, list) or
                       isinstance(subbuilders, tuple) else [])

        # Create the subbuilders
        if crop or crop_percentage:
            crop = crop_percentage or crop
            pdfcrop = PdfCrop(env, crop=crop, **kwargs)
            subbuilders.append(pdfcrop)

        pdf2svg = Pdf2svg(env, **kwargs)
        subbuilders.append(pdf2svg)

        if scale:
            scalesvg = ScaleSvg(env, scale, **kwargs)
            subbuilders.append(scalesvg)

        super().__init__(env, subbuilders=subbuilders, **kwargs)
