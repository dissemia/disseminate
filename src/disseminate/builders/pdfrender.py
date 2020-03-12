"""
A builder to render a tex file to pdf.
"""
from .composite_builders import SequentialBuilder
from .pdflatex import Pdflatex
from .jinja_render import JinjaRender


class PdfRender(SequentialBuilder):
    """Render a tex file and render the pdf."""

    available = True

    outfilepath_ext = '.pdf'

    def __init__(self, env, context=None, template=None, infilepaths=None,
                 outfilepath=None, subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a render if no infilepath is specified
        if infilepaths is None and context is not None:
            # If no infilepaths are specified, we need to render one from
            # the context
            render_build = JinjaRender(env, context=context, target='.tex',
                                       template=template, **kwargs)
            subbuilders.append(render_build)

            # Set the infilepath for this builder to match the render_build, if
            # used, so that the Md5Decision is properly calculated
            infilepaths = render_build.infilepaths

        # Setup a Pdflatex builder
        pdf_build = Pdflatex(env, **kwargs)
        subbuilders.append(pdf_build)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)

    @property
    def outfilepath(self):
        # Use the render builder's outfilepath if None is specified. This is
        # because the render builder's outfilepath is a hash of the input text,
        # which is unique.
        if self._outfilepath is None:
            render_builders = [b for b in self.subbuilders
                               if isinstance(b, JinjaRender)]
            outfilepath = (render_builders[0].outfilepath.use_suffix('.pdf')
                           if render_builders else
                           SequentialBuilder.outfilepath.fget(self))
            self._outfilepath = outfilepath
        return self._outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value
