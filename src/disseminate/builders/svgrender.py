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

    def __init__(self, env, parameters=None, outfilepath=None, context=None,
                 template=None, subbuilders=None, use_cache=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a PdfRender if no infilepath is specified
        builder_cls = self.find_builder_cls(in_ext='.render', out_ext='.pdf')
        pdfrender = builder_cls(env, context=context, template=template,
                                parameters=parameters, use_cache=True,
                                **kwargs)
        subbuilders.append(pdfrender)
        self.subbuilder_for_outfilename = pdfrender

        # Use the parameter from the pdfrender.
        parameters = parameters or pdfrender.parameters

        # Setup a pdf->svg converter
        builder_cls = self.find_builder_cls(in_ext='.pdf', out_ext='.svg')
        pdf2svg = builder_cls(env, parameters=parameters, use_cache=True,
                              **kwargs)
        subbuilders.append(pdf2svg)

        super().__init__(env, parameters=parameters, outfilepath=outfilepath,
                         subbuilders=subbuilders, use_cache=use_cache,
                         **kwargs)
