"""
A builder to render a tex file and convert it to an svg.
"""
from .composite_builders import SequentialBuilder


class SvgRender(SequentialBuilder):
    """Render a tex file and render the svg."""

    available = True
    priority = 1000

    infilepath_ext = '.render'
    outfilepath_ext = '.svg'

    _render_builder = None

    def __init__(self, env, infilepaths=None, outfilepath=None, context=None,
                 template=None, subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a PdfRender if no infilepath is specified
        builder_cls = self.find_builder_cls(in_ext='.render', out_ext='.pdf')
        pdfrender = builder_cls(env, context=context, template=template,
                                **kwargs)
        subbuilders.append(pdfrender)
        self._render_builder = pdfrender

        # Use the infilepath from the pdfrender.
        infilepaths = infilepaths or pdfrender.infilepaths

        # Setup a pdf->svg converter
        builder_cls = self.find_builder_cls(in_ext='.pdf', out_ext='.svg')
        pdf2svg = builder_cls(env, **kwargs)
        subbuilders.append(pdf2svg)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    @property
    def outfilepath(self):
        # Use the render builder's outfilepath if None is specified. This is
        # because the render builder's outfilepath is a hash of the input text,
        # which is unique.
        if self._outfilepath is None:
            render_builder = self._render_builder
            outfilepath = (render_builder.outfilepath.use_suffix('.svg')
                           if render_builder else
                           SequentialBuilder.outfilepath.fget(self))
            self._outfilepath = outfilepath
        return self._outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value
