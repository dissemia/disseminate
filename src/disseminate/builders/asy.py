"""
Builder for asymptote (.asy) files
"""
from .builder import Builder


class Asy2pdf(Builder):
    """A builder to convert from asy to pdf."""

    action = "asy -safe -f pdf -o {builder.outfilepath} {builder.infilepaths}"
    available = False
    priority = 1000
    required_execs = ('asy',)

    infilepath_ext = '.asy'
    outfilepath_ext = '.pdf'

