"""
A build environment to determine which build to use.
"""
from .deciders import Decider
from .scanners import Scanner
from ..document import Document
from ..utils.classes import weakattr
from ..paths import SourcePath
from .. import settings


class Environment(object):
    """A environment owns a root document and builds and renders needed
    files and documents."""

    builders = None
    decider = None
    scanner = None

    context = weakattr()
    root_documents = None
    target_root = None

    _cache_path = None
    _concrete_builders = None

    def __init__(self, src_filepath=None, target_root=None, context=None):
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
        if src_filepath:
            root_document = Document(src_filepath=src_filepath,
                                     target_root=target_root)
            self.root_document = root_document

        # Setup the builders
        self.context = context
        self.builders = []
        self.target_root = target_root or context['target_root']

    @property
    def cache_path(self):
        if self._cache_path is None:
            cache_path = SourcePath(project_root=self.target_root,
                                    subpath=settings.cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_path = cache_path
        return self._cache_path

    def get_builder(self, document_target, context=None):
        pass

