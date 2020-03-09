"""
A CompositeBuilder for html files.
"""
from .target_builder import TargetBuilder
from ..copy import Copy
from ...paths import SourcePath, TargetPath


class HtmlBuilder(TargetBuilder):
    """A builder for html files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.html'

    def __init__(self, env, context, **kwargs):
        super().__init__(env, context, target='.html', **kwargs)

        # Add copy builders for extra dependencies
        target_root = self.outfilepath.target_root
        target = self.outfilepath.target
        for ext in ('*.css',):
            copy_subbuilders = []
            for subbuilder in self.subbuilders:
                filepaths = [filepath for filepath in subbuilder.infilepaths
                             if isinstance(filepath, SourcePath) and
                             filepath.match(ext)]
                for filepath in filepaths:
                    subpath = filepath.subpath
                    target_filepath = TargetPath(target_root=target_root,
                                                 target=target,
                                                 subpath=subpath)
                    copy = Copy(env, infilepaths=filepath,
                                outfilepath=target_filepath)
                    copy_subbuilders.append(copy)
            self.subbuilders += copy_subbuilders

    def add_build(self, *args, **kwargs):
        super().add_build(document_target='.html', *args, **kwargs)

