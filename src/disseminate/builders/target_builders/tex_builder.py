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

    def __init__(self, env, document, **kwargs):
        super().__init__(env, document, target='.tex', **kwargs)

    def add_build(self, *args, **kwargs):
        super().add_build(document_target='.tex', *args, **kwargs)

