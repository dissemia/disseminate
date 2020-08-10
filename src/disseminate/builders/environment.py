"""
A build environment to determine which build to use.
"""
from itertools import chain
import pathlib

from .deciders import Decider
from .scanners import Scanner
from ..document import Document
from ..paths import SourcePath, TargetPath
from .. import settings


class Environment(object):
    """A project environment for rendering documents using builders.

    The build project environment has the following tasks:
        1. Setup the project_root and target_root
        2. Setup the default decider for builders
        3. Setup the default scanner for builders
        4. Setup the root document.

    Parameters
    ----------
    src_filepath : Union[str, :obj:`pathlib.Path`]
        The path for the disseminate source file of the root document.
    target_root : Optional[Union[str, :obj:`pathlib.Path`]]
        The (optional) path for the output root directory.
    parent_context : Optional[:obj:`.context.BaseContext`]
        The document context to use as the parent_context for the root document.
        Typically, the default_context from the settings is used as the parent
        context.
    """

    decider = None
    scanner = None

    root_document = None
    context = None
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

        # Setup the paths for the parent_context
        if not isinstance(src_filepath, SourcePath):
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

    def __repr__(self):
        return "Environment({})".format(self.project_root)

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
        """The path to the directory for storing cached files."""
        if self._cache_path is None:
            cache_path = SourcePath(project_root=self.target_root,
                                    subpath=settings.cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_path = cache_path
        return self._cache_path

    @property
    def media_path(self):
        """The path for to prepend to subpaths for media files."""
        if self.context:
            return self.context.get('media_path', None)
        return None

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
        return 'done'

    @staticmethod
    def _get_src_filepaths(root_path='',
                           document_extension=settings.document_extension):
        """Find the root src_filepaths from a given root_path"""
        # Create a glob pattern to get all of the disseminate files in the path
        # and remove the filenames to retain the unique paths. Convert the paths
        # to strings so that they can be sorted more easily.
        glob_pattern = pathlib.Path('**', '*' + document_extension)
        paths = {p.parent for p in root_path.glob(str(glob_pattern))}

        # Only keep entries that are basepaths
        basepaths = set()

        for path in paths:
            # See if its a base path based on whether any of its parent is
            # already located in the paths
            parents = path.parents
            if any(parent in paths for parent in parents):
                continue

            # The basepath is unique; add it to basepaths
            basepaths.add(path)

        # Generate the unique root paths as pathlib.Path objects.
        project_paths = [SourcePath(project_root=basepath)
                         for basepath in basepaths]

        src_filepaths = []

        for project_path in project_paths:
            # Find the src_filepaths for the root documents (non-recursive)
            glob_pattern = pathlib.Path('*' + document_extension)
            glob = list(project_path.glob(str(glob_pattern)))
            subpaths = [filepath.relative_to(project_path) for filepath in glob]
            src_filepaths += [SourcePath(project_root=project_path,
                                         subpath=subpath)
                              for subpath in subpaths]
        return src_filepaths

    @staticmethod
    def create_environments(root_path='', target_root=None,
                            document_extension=settings.document_extension):
        """Create environments from root documents found in the given root_path.

        Parameters
        ----------
        root_path : Optional[Union[str, :obj:`pathlib.Path`]]
            The path to search for root documents. By default, it is the
            current directory.
        target_root : Optional[Union[str, :obj:`pathlib.Path`]]
            The (optional) path for the output root directory.
        document_extension : Optional[str]
            The file extension for disseminate documents. ex: '.dm'

        Returns
        -------
        environments : List[:obj:`.builders.Environment`]
        """
        # expand the user for the subpath directory
        path = pathlib.Path(root_path).expanduser()

        # Get the src_filepaths for the root documents
        if path.is_file():
            # src_filepaths from the file directly
            src_filepaths = [SourcePath(project_root=path.parent,
                                        subpath=path.name)]
        else:
            # or through the directory with glob patterns (_get_src_filepaths)
            get_fps = Environment._get_src_filepaths
            fps = get_fps(root_path=path,
                          document_extension=document_extension)
            src_filepaths = fps

        return [Environment(src_filepath=src_filepath, target_root=target_root)
                for src_filepath in src_filepaths]
