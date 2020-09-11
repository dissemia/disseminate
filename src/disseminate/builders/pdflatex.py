"""
A builder to convert from TEX to PDF
"""
from .builder import Builder


class Pdflatex(Builder):
    """Compile a latex document into pdf using pdflatex"""

    action = ("pdflatex "
              "-interaction=nonstopmode "  # Do not hang on error
              "-halt-on-error "  # Do not hang on error
              "-output-directory={builder.cache_path} "  # dir for temp files
              "-jobname={builder.jobname} "  # filename of output file
              "{builder.infilepaths}")  # tex file to use

    available = True
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
