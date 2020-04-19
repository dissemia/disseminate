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

    def __init__(self, env, infilepaths=None, outfilepath=None, context=None,
                 template=None, subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a PdfRender if no infilepath is specified
        builder_cls = self.find_builder_cls(in_ext='.render', out_ext='.pdf')
        pdfrender = builder_cls(env, context=context, template=template,
                                **kwargs)
        subbuilders.append(pdfrender)
        self.subbuilder_for_outfilename = pdfrender

        # Use the infilepath from the pdfrender.
        infilepaths = infilepaths or pdfrender.infilepaths

        # Setup a pdf->svg converter
        builder_cls = self.find_builder_cls(in_ext='.pdf', out_ext='.svg')
        pdf2svg = builder_cls(env, **kwargs)
        subbuilders.append(pdf2svg)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)