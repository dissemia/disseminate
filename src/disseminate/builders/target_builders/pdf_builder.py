"""
A CompositeBuilder for pdf files.
"""
from .target_builder import TargetBuilder
from ..composite_builders import SequentialBuilder
from .tex_builder import TexBuilder
from ..pdflatex import Pdflatex


class PdfBuilder(TargetBuilder):
    """A builder for Pdf files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.pdf'

    add_parallel_builder = False
    add_render_builder = False

    _tex_builder = None
    _pdf_builder = None

    def __init__(self, env, context, infilepaths=None, outfilepath=None,
                 subbuilders=None, **kwargs):
        # Setup the subbuilders
        subbuilders = subbuilders or []

        # Find the tex_builder or create one.
        builders = context.setdefault('builders', dict())
        tex_builder = builders.setdefault('.tex',
                                          TexBuilder(env=env, context=context,
                                                     target='tex',
                                                     **kwargs))
        self._tex_builder = tex_builder
        subbuilders.append(tex_builder)

        # Now add a Pdf converter
        pdf_builder = Pdflatex(env=env, target='pdf', **kwargs)
        self._pdf_builder = pdf_builder
        subbuilders.append(pdf_builder)

        super().__init__(env=env, context=context, infilepaths=infilepaths,
                         outfilepath=outfilepath, subbuilders=subbuilders,
                         **kwargs)

        # Setup the paths
        pdf_builder.infilepaths = [tex_builder.outfilepath]
        pdf_builder.outfilepath = self.outfilepath

    def add_build(self, infilepaths, outfilepath=None, context=None, **kwargs):
        return self._tex_builder.add_build(infilepaths=infilepaths,
                                           outfilepath=outfilepath,
                                           context=context, **kwargs)
