"""
A build environment to determine which build to use.
"""
from inspect import isabstract

from .builder import Builder
from .deciders import Decider
from ..utils.classes import all_subclasses, weakattr
from ..paths import SourcePath
from .. import settings


class Environment(object):

    context = weakattr()
    decider = None
    target_root = None

    _cache_path = None
    _concrete_builders = None

    def __init__(self, context):
        context.is_valid('target_root')
        self.context = context
        self.target_root = context['target_root']

        # Setup the decider
        decider_cls = [cls for cls in Decider.__subclasses__()
                       if cls.__name__ == settings.default_decider]
        assert decider_cls, ("The decider class '{}' does not "
                             "exist".format(settings.default_decider))
        decider_cls = decider_cls[0]
        self.decider = decider_cls(env=self)

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
