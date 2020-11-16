"""
A TargetBuilder for html files.
"""
from .target_builder import TargetBuilder
from ..copy import Copy
from ...paths import TargetPath
from ... import settings


class HtmlBuilder(TargetBuilder):
    """A builder for html files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.html'
    ext_wildcards = {'*' + ext for ext in settings.tracked_deps['.html']}

    def __init__(self, env, context, **kwargs):
        super().__init__(env=env, context=context, **kwargs)

        # Add copy builders for extra dependencies, like css files
        target_root = env.target_root
        cache_path = env.cache_path
        target = self.outfilepath_ext

        for ext in self.ext_wildcards:
            copy_subbuilders = []
            for subbuilder in self.subbuilders:
                # Get the filepaths found from the render builder. These
                # should be copied over as needed. (ex: '.css' files)
                filepaths = [filepath for filepath in subbuilder.infilepaths
                             if filepath.match(ext)]

                for filepath in filepaths:
                    subpath = filepath.subpath

                    # Place the copied file either in the target_root directory
                    # or the cache_path directory, depending on whether
                    # self.use_cache is enabled (True).
                    root_path = cache_path if self.use_cache else target_root

                    # Reconstruct the path for the copied file in its
                    # destination directory
                    target_filepath = TargetPath(target_root=root_path,
                                                 target=target,
                                                 subpath=subpath)

                    # Create the copy builder and place it in the copy builders
                    # list to be added to the parallel builder
                    copy = Copy(env, parameters=filepath,
                                outfilepath=target_filepath)
                    copy_subbuilders.append(copy)

            # Add these copy builders to the parallel builders
            self._parallel_builder.subbuilders += copy_subbuilders
