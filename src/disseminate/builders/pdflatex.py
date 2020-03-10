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


class PdflatexDraft(Pdflatex):
    """Compile a latex document using pdflatex in draft mode"""

    action = ("pdflatex "
              "-interaction=nonstopmode "  # Do not hang on error
              "-halt-on-error "  # Do not hang on error
              "-draftmode "  # compile in draft mode
              "-output-directory={builder.cache_path} "  # dir for temp files
              "-jobname={builder.jobname} "  # filename of output file
              "{builder.infilepaths}")  # tex file to use


class PdfRender(SequentialBuilder):
    """Render a tex file and render the pdf."""

    available = True

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

        # Setup a (draftmode) Pdflatex builder
        # pdf_draft_build = PdflatexDraft(env, **kwargs)
        # subbuilders.append(pdf_draft_build)

        # Setup a Pdflatex builder
        pdf_build = Pdflatex(env, **kwargs)
        subbuilders.append(pdf_build)

        super().__init__(env, infilepaths=infilepaths, outfilepath=outfilepath,
                         subbuilders=subbuilders, **kwargs)