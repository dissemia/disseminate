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

    _render_builder = None

    def __init__(self, env, context=None, template=None, infilepaths=None,
                 outfilepath=None, subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a render if no infilepath is specified
        if infilepaths is None and context is not None:
            # If no infilepaths are specified, we need to render one from
            # the context
            render_cls = self.find_builder_cls(in_ext='.render')
            render_build = render_cls(env, context=context, render_ext='.tex',
                                      template=template, **kwargs)
            subbuilders.append(render_build)
            self._render_builder = render_build

            # Set the infilepath for this builder to match the render_build, if
            # used, so that the Md5Decision is properly calculated
            infilepaths = render_build.infilepaths

        # Setup a pdf builder
        pdf_build_cls = self.find_builder_cls(in_ext='.tex', out_ext='.pdf')
        pdf_build = pdf_build_cls(env, **kwargs)
        subbuilders.append(pdf_build)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    @property
    def outfilepath(self):
        # Use the render builder's outfilepath if None is specified. This is
        # because the render builder's outfilepath is a hash of the input text,
        # which is unique.
        if self._outfilepath is None:
            render_builder = self._render_builder
            outfilepath = (render_builder.outfilepath.use_suffix('.pdf')
                           if render_builder else
                           SequentialBuilder.outfilepath.fget(self))

            self._outfilepath = outfilepath
        return self._outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value
