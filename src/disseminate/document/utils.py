import pathlib

from .document import Document
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

    Notes
    -----
    This function doesn't actually load documents. If there are multiple
    disseminate files in the project root path, even if one is a root document
    and the others are not, they will all be returned.
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
                        target_root=None,
                        document_extension=settings.document_extension):
    """Load the root documents from the project paths for the given path.

    Parameters
    ----------
    path : Optional[Union[:obj:`pathlib.Path`, str]]
        The path to search for root documents.
        By default, it is the current directory.
        If the path is specified for a root document, that will be used
        directly.
    target_root : Optional[Union[:obj:`TargetPath <.paths.TargetPath>`, str]]
        The path for the rendered target files. Subdirectories for the targets
        will be created. (ex: 'html' 'tex')
        By default, if not specified, the target_root will be one directory
        above the project_root.
    document_extension : Optional[str]
        The source markup document extension. ex: '.dm'

    Returns
    -------
    root_documents : List[:obj:`Document <.Document>`]
        A list containing root documents.
    """
    # Convert the path to a pathlib.Path object
    path = pathlib.Path(path)

    # Check to see if a filepath was pass or just a directory
    if path.suffix and path.is_file():
        # In this case a filepath was passed. Use it directly to create the
        # document
        src_filepaths = [path]
    else:
        # Otherwise, parse the path as a directory
        # Find the root src_filepaths
        ext = document_extension
        src_filepaths = find_root_src_filepaths(path=path,
                                                document_extension=ext)

    # Create the root documents.
    # The src_filepaths are converterted to strings to properly parse the
    # project_root, since we only have pathlib.Path objects at this point--
    # not SourcePath objects. The Document __init__ properly create SourcePaths
    # that parse the project_root from the subpath.
    root_documents = [Document(src_filepath=str(src_filepath),
                               target_root=target_root)
                      for src_filepath in src_filepaths]

    # Remove "root documents" that are included by other root documents--i.e.
    # documents that aren't root_documents

    # Create a dict with root_document src_filepaths as the keys and sub
    # document src_filepaths as the values.
    subdoc_src_filepaths = set()
    for doc in root_documents:
        root_src_filepath = doc.src_filepath
        values = doc.documents_dict(only_subdocuments=True, recursive=True)
        subdoc_src_filepaths |= set(values.keys())

    # Remove "root documents" that are sub-documents to other root documents
    root_documents = [doc for doc in root_documents
                      if doc.src_filepath not in subdoc_src_filepaths]

    return root_documents
