"""
Builder for tex to pdf using latexmk
"""
from .builder import Builder


class Latexmk(Builder):
    """Compile a latex document into pdf using latexmk

    .. note:: This builder has been disabled by default because it fails about
              20% of the time with this system's ThreadPoolExecutor
              implementation.
    """

    action = ("latexmk "
              "-pdf "  # output pdf
              "-norc "  # do not use latexmkrc config
              "-f "  # continue past errors
              "-bibtex- "  # don't use bibtex
              "-jobname={builder.jobname} "  # filename of output file
              "-output-directory={builder.cache_path} "  # dir for temp files
              "{builder.infilepaths}")  # tex file to use

    available = False
    priority = 5000
    required_execs = ('latexmk', 'pdflatex')

    infilepath_ext = '.tex'
    outfilepath_ext = '.pdf'

    @property
    def cache_path(self):
        return self.outfilepath.parent

    @property
    def jobname(self):
        return self.outfilepath.stem
