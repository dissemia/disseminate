"""
Functions to load projects in a session.
"""
from .store import store
from ..builders.environment import Environment


def load_projects(request):
    """Retrieve the root documents from the store.

    Returns
    -------
    root_documents : List[:obj:`Document <.Document`]
        The loaded root documents.
    """
    # Get the session and config
    config = request.app.config

    # Make sure the project list is loaded
    if 'root_documents' not in store:
        # Get project_filenames
        in_path = config.get('in_path', '')
        out_dir = config.get('out_dir', None)

        # Fetch the root documents
        envs = Environment.create_environments(root_path=in_path)
        docs = [env.root_document for env in envs]
        store['root_documents'] = docs

    # See if any of the docs need to be rendered
    [doc.render() for doc in store['root_documents']]
    return store['root_documents']
