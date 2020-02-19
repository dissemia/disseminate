"""
A build environment to determine which build to use.
"""
from inspect import isabstract

from .builder import Builder
from ..utils.classes import all_subclasses, weakattr
from ..paths import SourcePath
from .. import settings


class Environment(object):

    context = weakattr()
    target_root = None

    _cache_path = None
    _concrete_builders = None

    def __init__(self, context):
        context.is_valid('target_root')
        self.context = context
        self.target_root = context['target_root']

    @property
    def cache_path(self):
        if self._cache_path is None:
            cache_path = SourcePath(project_root=self.target_root,
                                    subpath=settings.cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_path = cache_path
        return self._cache_path

    @classmethod
    def get_builder(cls, infilepath, document_target):
        # See if a list of available builders is set yet
        if cls._concrete_builders is None:
            # Get a listing of concrete builder classes
            builders = all_subclasses(Builder)

            # Remove those that are abstract
            builders = [builder for builder in builders
                        if not isabstract(builder)]
