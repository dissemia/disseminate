"""
A build environment to determine which build to use.
"""
from .deciders import Decider
from .scanners import Scanner
from .target_builders import HtmlBuilder, TexBuilder
from .composite_builders import ParallelBuilder
from ..document import Document
from ..paths import SourcePath
from .. import settings


class Environment(object):
    """A environment owns a root document and builds and renders needed
    files and documents."""

    builders = None
    decider = None
    scanner = None

    root_document = None
    target_root = None

    _cache_path = None
    _concrete_builders = None

    def __init__(self, src_filepath=None, target_root=None,
                 parent_context=None):

        # Setup the decider
        decider_cls = [cls for cls in Decider.__subclasses__()
                       if cls.__name__ == settings.default_decider]
        assert decider_cls, ("The decider class '{}' does not "
                             "exist".format(settings.default_decider))
        decider_cls = decider_cls[0]
        self.decider = decider_cls(env=self)

        # Setup the scanner
        self.scanner = Scanner

        # Setup the root document
        root_document = Document(src_filepath=src_filepath,
                                 target_root=target_root,
                                 parent_context=parent_context)
        self.root_document = root_document
        self.context = root_document.context

        # Setup the builders
        self.builders = []

        # Setup paths
        target_root = (target_root or
                       root_document.context.get('target_root', None))
        self.target_root = target_root

    @property
    def cache_path(self):
        if self._cache_path is None:
            cache_path = SourcePath(project_root=self.target_root,
                                    subpath=settings.cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_path = cache_path
        return self._cache_path

    def build(self, complete=True):
        """Run the build"""
        # Reload the root_document
        root_document = self.root_document
        root_document.load()

        # Create target builders for each document
        builds = []
        for target_builder, target in ((HtmlBuilder, '.html'),
                                       (TexBuilder, '.tex')):
            subbuilders = []
            docs = root_document.documents_list(only_subdocuments=False,
                                                recursive=True)
            for doc in docs:
                if target in doc.targets:
                    build = target_builder(env=self, context=doc.context)
                    subbuilders.append(build)

            # Add the builds to a parallel build so that they can be created
            # at the same time
            parallel_build = ParallelBuilder(env=self, subbuilders=subbuilders)
            builds.append(parallel_build)

        # Run the builds in sequence. Some targets may depend on others
        # (ex: pdf depends on tex)
        for build in builds:
            build.build()

    def get_builder(self, document_target, context=None):
        pass

