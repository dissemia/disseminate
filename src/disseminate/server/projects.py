"""
Functions to load projects in a session.
"""
from .store import store
from ..document.utils import load_root_documents


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
        docs = load_root_documents(path=in_path, target_root=out_dir)
        store['root_documents'] = docs

    # See if any of the docs need to be rendered
    [doc.render() for doc in store['root_documents']]
    return store['root_documents']
