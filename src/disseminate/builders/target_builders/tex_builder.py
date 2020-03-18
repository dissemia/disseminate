"""
A CompositeBuilder for tex files.
"""
from .target_builder import TargetBuilder


class TexBuilder(TargetBuilder):
    """A builder for tex files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.tex'

    def add_build(self, infilepaths, outfilepath=None, context=None, **kwargs):
        return super().add_build(document_target='.tex',
                                 infilepaths=infilepaths,
                                 outfilepath=outfilepath, context=context,
                                 **kwargs)
