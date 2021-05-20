"""
A builder to render a tex file to pdf.
"""
from .composite_builders import SequentialBuilder


class PdfRender(SequentialBuilder):
    """Render a tex file and render the pdf."""

    available = True
    priority = 1000

    infilepath_ext = '.render'  # dummy extension for find_builder_cls
    outfilepath_ext = '.pdf'

    def __init__(self, env, context=None, template=None, parameters=None,
                 outfilepath=None, subbuilders=None, use_cache=None,
                 **kwargs):

        # Setup the arguments
        parameters = parameters or []
        subbuilders = subbuilders or []

        # Setup a render if a context is specified
        if context is not None:
            render_cls = self.find_builder_cls(in_ext='.render')
            render_build = render_cls(env, context=context, render_ext='.tex',
                                      template=template, parameters=parameters,
                                      use_cache=True, **kwargs)

            # Set the parameters for this builder to match the render_build, if
            # used, so that the Md5Decision is properly calculated
            parameters += render_build.parameters

            subbuilders.append(render_build)
            self.subbuilder_for_outfilename = render_build

        # Setup a pdf builder
        pdf_build_cls = self.find_builder_cls(in_ext='.tex', out_ext='.pdf')
        pdf_build = pdf_build_cls(env, use_cache=True, **kwargs)
        subbuilders.append(pdf_build)
        super().__init__(env, parameters=parameters, outfilepath=outfilepath,
                         subbuilders=subbuilders, use_cache=use_cache,
                         **kwargs)
