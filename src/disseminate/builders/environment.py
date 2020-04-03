"""
A build environment to determine which build to use.
"""
from copy import deepcopy
from itertools import chain
import pathlib

from .deciders import Decider
from .scanners import Scanner
from ..document import Document
from ..paths import SourcePath, TargetPath
from .. import settings


class Environment(object):
    """A environment owns a root document and builds and renders needed
    files and documents."""

    decider = None
    scanner = None

    root_document = None
    project_root = None
    target_root = None

    _cache_path = None
    _concrete_builders = None

    def __init__(self, src_filepath, target_root=None, parent_context=None):

        # Setup the decider
        decider_cls = [cls for cls in Decider.__subclasses__()
                       if cls.__name__ == settings.default_decider]
        assert decider_cls, ("The decider class '{}' does not "
                             "exist".format(settings.default_decider))
        decider_cls = decider_cls[0]
        self.decider = decider_cls(env=self)

        # Setup the scanner
        self.scanner = Scanner

        # Setup the parent_context for the root_document

        # Setup the paths for the parent_context
        if not isinstance(src_filepath, pathlib.Path):
            # Make sure the src_filepath is a Source path
            src_filepath = pathlib.Path(src_filepath)
            src_filepath = SourcePath(project_root=src_filepath.parent,
                                      subpath=src_filepath.name)
        project_root = src_filepath.project_root
        self.project_root = project_root

        if target_root is not None:
            # Make sure the target_root is a TargetPath
            target_root = TargetPath(target_root=target_root)
        else:
            target_root = self.get_target_root(project_root)
        self.target_root = target_root

        # Setup the root document
        root_document = Document(src_filepath=src_filepath,
                                 parent_context=parent_context,
                                 environment=self)
        self.context = root_document.context
        self.root_document = root_document

    @staticmethod
    def get_target_root(project_root):
        """Determine the target_root directory from the project_root."""
        if project_root.match(settings.document_src_directory):
            # If the project_root is in a src directory, use the directory above
            # this directory
            return TargetPath(target_root=project_root.parent)
        else:
            # Otherwise just use the same directory as the src directory
            return TargetPath(target_root=project_root)

    @property
    def cache_path(self):
        if self._cache_path is None:
            cache_path = SourcePath(project_root=self.target_root,
                                    subpath=settings.cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_path = cache_path
        return self._cache_path

    def collect_target_builders(self):
        """Return all target builders for the root_document and all
        sub-documents."""
        documents = self.root_document.documents_list(recursive=True)
        return chain(*[doc.context['builders'].values()
                       if 'builders' in doc.context else []
                       for doc in documents])

    def build(self):
        target_builders = self.collect_target_builders()
        for target_builder in target_builders:
            target_builder.build(complete=True)

