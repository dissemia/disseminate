"""
Functions to load projects in a session.
"""
from pathlib import Path

from bottle import request

from ..document.utils import load_root_documents

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
template_path = Path(__file__).parent.parent / 'templates' / 'server'


def load_projects():
    """Retrieve the root documents from the session.

    Returns
    -------
    root_documents : List[:obj:`Document <.Document`]
        The loaded root documents.
    """
    # Get the session
    session = request.environ.get('session')

    # Make sure the project list is loaded
    if session and 'root_documents' not in session:
        # Get the root directory
        config = request.app.config
        in_directory = config.get('in_directory', '.')

        # Fetch the root documents
        docs = load_root_documents(path=in_directory)
        session['root_documents'] = docs
        session['target_roots'] = [doc.target_root for doc in docs]

    return session.get('root_documents', []) if session else []


def target_roots():
    """Retrieve the target root paths from the session.

    Returns
    -------
    target_root_paths : List[:obj:`TargetPath <.paths.TargetPath>`]
        The target root paths for the loaded root documents.
    """
    # Get the session
    session = request.environ.get('session')

    if session and 'target_roots' not in session:
        load_projects()

    return session.get('target_roots', []) if session else []


def static_paths():
    """Retrieve the static file paths from the session.

    Returns
    -------
    static_paths : List[:obj:`pathlib.Path`]
        The static file paths.
    """
    # Get the session
    session = request.environ.get('session')

    if session and 'static_paths' not in session:
        paths = []
        paths += target_roots()
        paths.append(template_path)
        session['static_paths'] = paths

    return session.get('static_paths', []) if session else []
