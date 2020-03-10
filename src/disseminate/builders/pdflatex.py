"""
A builder to convert from TEX to PDF
"""
from .builder import Builder
from .composite_builders import SequentialBuilder
from .jinja_render import JinjaRender


class Pdflatex(Builder):
    """Compile a latex document into pdf using pdflatex"""

    action = ("pdflatex "
              "-interaction=nonstopmode "  # Do not hang on error
              "-halt-on-error "  # Do not hang on error
              "-output-directory={builder.cache_path} "  # dir for temp files
              "-jobname={builder.jobname} "  # filename of output file
              "{builder.infilepaths}")  # tex file to use

    available = False
    priority = 1000
    required_execs = ('pdflatex',)

    infilepath_ext = '.tex'
    outfilepath_ext = '.pdf'

    @property
    def cache_path(self):
        return self.outfilepath.parent

    @property
    def jobname(self):
        return self.outfilepath.stem


class PdfRender(SequentialBuilder):
    """Render a tex file and render the pdf."""

    def __init__(self, env, context=None, infilepaths=None, outfilepath=None,
                 subbuilders=None, **kwargs):

        # Setup the arguments
        subbuilders = subbuilders or []

        # Setup a render if no infilepath is specified
        if infilepaths is None and context is not None:
            # If no infilepaths are specified, we need to render one from
            # the context
            render_build = JinjaRender(env, context=context, **kwargs)
            subbuilders.append(render_build)

        # Setup a Pdflatex builder
        pdf_build = Pdflatex(env, **kwargs)
        subbuilders.append(pdf_build)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)
