"""
Functions to load projects in a session.
"""
import flask.globals as gbl

from .store import store
from ..document import Document


def load_projects():
    """Retrieve the root documents from the session.

    Returns
    -------
    root_documents : List[:obj:`Document <.Document`]
        The loaded root documents.
    """
    # Get the session and config
    config = gbl.current_app.config

    # Make sure the project list is loaded
    if 'root_documents' not in store:
        # Get project_filenames
        project_filenames = config.get('project_filenames', [])
        out_dir = config.get('out_dir', None)

        # Fetch the root documents
        docs = [Document(src_filepath=project_filename, target_root=out_dir)
                for project_filename in project_filenames]

        store['root_documents'] = docs
        store['target_roots'] = [doc.target_root for doc in docs]

    # See if any of the docs need to be rendered
    [doc.render() for doc in store['root_documents']]
    return store['root_documents']


def target_roots():
    """Retrieve the target root paths from the session.

    Returns
    -------
    target_root_paths : List[:obj:`TargetPath <.paths.TargetPath>`]
        The target root paths for the loaded root documents.
    """
    if 'target_roots' not in store:
        load_projects()

    return store['target_roots']
