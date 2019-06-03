import pathlib
from datetime import datetime

from .document import Document
from ..formats import html_tag
from ..paths import SourcePath
from .. import settings


def find_project_paths(path='', document_extension=settings.document_extension):
    """Find the project paths within the given path.

    This function will only return the root project paths for directories
    containing disseminate files (i.e. files with the document_extension)

    Parameters
    ----------
    path : Optional[Union[:obj:`pathlib.Path`, str]]
        The path to search. By default, it is the current directory.
    document_extension : Optional[str]
        The source markup document extension. ex: '.dm'

    Returns
    -------
    project_paths : List[:obj:`SourcePath <.paths.SourcePath>`]
        A list of project paths paths.
    """
    # expand the user for the subpath directory
    path = pathlib.Path(path).expanduser()

    # Create a glob pattern to get all of the disseminate files in the path
    # and remove the filenames to retain the unique paths. Convert the paths
    # to strings so that they can be sorted more easily.
    glob_pattern = pathlib.Path('**', '*' + document_extension)
    paths = {p.parent for p in path.glob(str(glob_pattern))}

    # Only keep entries that are basepaths
    basepaths = set()

    for path in paths:
        # See if its a base path based on whether any of its parent is already
        # located in the paths
        parents = path.parents
        if any(parent in paths for parent in parents):
            continue

        # The basepath is unique; add it to basepaths
        basepaths.add(path)

    # Return the unique root paths as pathlib.Path objects.
    return [SourcePath(project_root=basepath) for basepath in basepaths]


def find_root_src_filepaths(path='',
                            document_extension=settings.document_extension):
    """Find the src_filepaths for root documents in the given path.

    Parameters
    ----------
    path : Optional[Union[:obj:`pathlib.Path`, str]]
        The path to search. By default, it is the current directory.
    document_extension : Optional[str]
        The source markup document extension. ex: '.dm'

    Returns
    -------
    root_src_filepaths : List[:obj:`patlib.Path`]
        A list containing root document src_filepaths.
    """
    src_filepaths = []

    # Get the project paths and find the disseminate files in the root of these
    # paths
    project_paths = find_project_paths(path=path,
                                       document_extension=document_extension)

    for project_path in project_paths:
        # Find the src_filepaths for the root documents (non-recursive)
        glob_pattern = pathlib.Path('*' + document_extension)
        src_filepaths += list(project_path.glob(str(glob_pattern)))

    return src_filepaths


def load_root_documents(path='',
                        document_extension=settings.document_extension):
    """Load the root documents from the project paths for the given path.

    Parameters
    ----------
    path : Optional[Union[:obj:`pathlib.Path`, str]]
        The path to search. By default, it is the current directory.
    document_extension : Optional[str]
        The source markup document extension. ex: '.dm'

    Returns
    -------
    root_documents : List[:obj:`Document <.Document>`]
        A list containing root documents.
    """
    return [Document(str(src_filepath)) for src_filepath in
            find_root_src_filepaths(path=path,
                                    document_extension=document_extension)]


def translate_path(path, documents):
    """Translate a path to a render path.

    Given a src_filepath or target_filepath and documents, this function finds
    the corresponding render path for a path relative to the project_root or
    target_root. The file in the given render_path exists.

    Parameters
    ----------
    path : str
        The path relative to project_root or target_root.
    documents : List[:obj:`Document <.Document>`]
        The documents whose paths should be checked.

    Returns
    -------
    render_path : Union[str, None]
    """
    # Strip leading '/' if present
    if isinstance(path, str):
        path = path if not path.startswith('/') else path[1:]

    # Make sure the path is a path object
    path = pathlib.Path(path)

    # See if the path is valid as is.
    if path.is_file():
        return path

    # Loop through the documents and see if a project_root or target_root
    # path is found.
    for document in documents:
        # Try constructing a render src_filepath
        src_filepath = document.project_root / path
        if src_filepath.is_file():
            return src_filepath

        # Check to see if the path can be constructed to a target_filepath
        targets = set()
        for subdoc in document.documents_list(only_subdocuments=False,
                                              recursive=True):
            targets = subdoc.targets
            for target, target_filepath in targets.items():
                if target_filepath.match(str(path)):
                    return target_filepath

    return None
