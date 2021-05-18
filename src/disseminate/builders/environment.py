"""
A build environment to manage and execute builders.
"""
import pathlib
from itertools import chain

from .deciders import Decider
from .scanners import Scanner
from .composite_builders import ParallelBuilder
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
        The document context to use as the parent_context for the root
        document. Typically, the default_context from the settings is used as
        the parent context.
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
        project_root = SourcePath(project_root=src_filepath.project_root)
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

    @property
    def name(self):
        """The name of the environment"""
        root_doc = self.root_document
        src_filepath = (root_doc.src_filepath.subpath if root_doc is not None
                        else None)
        return str(src_filepath) if src_filepath is not None else ''

    @staticmethod
    def get_target_root(project_root):
        """Determine the target_root directory from the project_root."""
        if project_root.match(settings.document_src_directory):
            # If the project_root is in a src directory, use the directory
            # above this directory
            return TargetPath(target_root=project_root.parent)
        else:
            # Otherwise just use the same directory as the src directory
            return TargetPath(target_root=project_root)

    @staticmethod
    def _get_src_filepaths(root_path='',
                           document_extension=settings.document_extension):
        """Find the root src_filepaths from a given root_path"""
        # Create a glob pattern to get all of the disseminate files in the path
        # and remove the filenames to retain the unique paths. Convert the
        # paths to strings so that they can be sorted more easily.
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
            subpaths = [filepath.relative_to(project_path)
                        for filepath in glob]
            src_filepaths += [SourcePath(project_root=project_path,
                                         subpath=subpath)
                              for subpath in subpaths]
        return src_filepaths

    @staticmethod
    def create_environments(root_path='', target_root=None,
                            document_extension=settings.document_extension):
        """Create environments from root documents found in the given
        root_path.

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

    def create_root_builder(self, document=None):
        """Create a root parallel builder for the target builders of the given
        document or the root document.

        Parameters
        ----------
        document : Optional[:obj:`.document.Document`]
            The document to create a root builder for.

        Returns
        -------
        root_builder : :obj:`.composite_builders.ParallelBuilder`
            The root (parallel) builder.
        """
        root_builder = ParallelBuilder(env=self)
        root_builder.clear_done = True

        # Get all of the documents
        subbuilders = self.collect_target_builders(document=document)
        root_builder.subbuilders += subbuilders

        return root_builder

    def collect_target_builders(self, document=None):
        """Return all target builders for the root_document and all
        sub-documents.

        Parameters
        ----------
        document : Optional[:obj:`.document.Document`]
            The document to create a root builder for.

        Returns
        -------
        target_builders : List[:obj:`.builders.Builder`
            The list of target builders
        """
        document = document if document is not None else self.root_document
        documents = document.documents_list(only_subdocuments=False,
                                            recursive=True)
        return chain(*[doc.context['builders'].values()
                       if 'builders' in doc.context else []
                       for doc in documents])

    def build(self, complete=True):
        """Run the build.

        Parameters
        ----------
        complete : Optional[bool]
            If True, run the build until it has completed
            If False, start the build in the background.

        Returns
        -------
        status : str
            The current status of the build.
        """
        root_builder = self.create_root_builder()
        return root_builder.build(complete=complete)
