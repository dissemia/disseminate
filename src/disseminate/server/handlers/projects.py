"""
Functions to load projects in a session.
"""
import logging

from .store import store
from ...builders.environment import Environment


def load_projects(app):
    """Retrieve the root documents from the store.
    Returns
    -------
    root_documents : List[:obj:`Document <.Document`]
        The loaded root documents.
    """
    # Get the session and config
    settings = app.settings

    # Make sure the project list is loaded
    if 'root_documents' not in store:
        # Get project_filenames
        in_path = settings.get('in_path', '')

        # Fetch the root documents
        envs = Environment.create_environments(root_path=in_path)
        docs = [env.root_document for env in envs]

        # Log the loaded root documents
        for doc in docs:
            logging.debug("Loaded root document '{}'".format(doc))

        # Store the root documents in the global store
        store['root_documents'] = docs

    # See if any of the docs need to be built
    [doc.build() for doc in store['root_documents']]
    return store['root_documents']
