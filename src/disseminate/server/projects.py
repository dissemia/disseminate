"""
Functions to load projects in a session.
"""
from bottle import request

from ..document.utils import load_root_documents


def load_projects():
    # Get the root directory
    config = request.app.config
    in_directory = config.get('in_directory', '.')

    # Get the session
    session = request.environ.get('session')

    # Make sure the project list is loaded
    if session and 'root_documents' not in session:
        # Fetch the root documents
        docs = load_root_documents(path=in_directory)
        session['root_documents'] = docs

    return session['root_documents'] if session else None
