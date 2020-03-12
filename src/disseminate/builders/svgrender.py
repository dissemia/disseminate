"""
A builder to render a tex file and convert it to an svg.
"""
from .composite_builders import SequentialBuilder
from .pdfrender import PdfRender
from .pdf2svg import Pdf2SvgCropScale


class SvgRender(SequentialBuilder):
    """Render a tex file and render the svg."""

    available = True

    infilepath_ext = '.tex'
    outfilepath_ext = '.svg'

    def __init__(self, env, infilepaths=None, outfilepath=None, context=None,
                 template=None, subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a PdfRender if no infilepath is specified
        pdfrender = PdfRender(env, context=context, template=template, **kwargs)
        subbuilders.append(pdfrender)

        # Use the infilepath from the pdfrender.
        infilepaths = infilepaths or pdfrender.infilepaths

        # Setup a pdf->svg converter
        pdf2svg = Pdf2SvgCropScale(env, **kwargs)
        subbuilders.append(pdf2svg)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    @property
    def outfilepath(self):
        # Use the render builder's outfilepath if None is specified. This is
        # because the render builder's outfilepath is a hash of the input text,
        # which is unique.
        if self._outfilepath is None:
            render_builders = [b for b in self.subbuilders
                               if isinstance(b, PdfRender)]
            outfilepath = (render_builders[0].outfilepath.use_suffix('.svg')
                           if render_builders else
                           SequentialBuilder.outfilepath.fget(self))
            self._outfilepath = outfilepath
        return self._outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value
