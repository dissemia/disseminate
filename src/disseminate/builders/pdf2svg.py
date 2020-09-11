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

    def __init__(self, env, **kwargs):
        super().__init__(env, **kwargs)

        # Get the page number
        page_no = self.get_parameter('page') or self.get_parameter('page_no')
        try:
            self.page_no = int(page_no)
        except TypeError:
            pass

    def run_cmd_args(self):
        args = list(super().run_cmd_args())
        if isinstance(self.page_no, int):
            args += [self.page_no]
        return tuple(args)


class Pdf2SvgCropScale(SequentialBuilder):
    """A SequentialBuilder for Pdf2Svg that includes PdfCrop and ScaleSvg
    builders.
    """

    available = True
    priority = 1000
    infilepath_ext = '.pdf'
    outfilepath_ext = '.svg'

    def __init__(self, env, parameters=None, subbuilders=None, use_cache=None,
                 **kwargs):
        # Setup parameters. The parameters list should be a copy.
        subbuilders = (list(subbuilders) if (isinstance(subbuilders, list) or
                       isinstance(subbuilders, tuple)) else [])
        parameters = parameters if parameters is not None else []
        parameters = (list(parameters) if isinstance(parameters, tuple) or
                      isinstance(parameters, list) else [parameters])

        # Create the subbuilders
        crop = self.get_parameter('crop', *parameters)
        crop = (crop if crop is not None else
                self.get_parameter('crop_percentage', *parameters))

        if crop is not None:
            pdfcrop = PdfCrop(env, parameters=parameters, use_cache=True,
                              **kwargs)
            subbuilders.append(pdfcrop)

        pdf2svg = Pdf2svg(env, use_cache=True, **kwargs)
        subbuilders.append(pdf2svg)

        scale = self.get_parameter('scale', *parameters)
        if scale is not None:
            scalesvg = ScaleSvg(env, parameters=parameters, use_cache=True,
                                **kwargs)
            subbuilders.append(scalesvg)

        super().__init__(env, parameters=parameters, subbuilders=subbuilders,
                         use_cache=use_cache, **kwargs)
