"""
Functions to load projects in a session.
"""
import flask.globals as gbl

from .store import store
from ..document.utils import load_root_documents


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
        # Get the root directory
        in_directory = config.get('in_directory', '.')

        # Fetch the root documents
        docs = load_root_documents(path=in_directory)
        store['root_documents'] = docs
        store['target_roots'] = [doc.target_root for doc in docs]

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
