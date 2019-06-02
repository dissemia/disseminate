"""
Functions for serving static files.
"""

from bottle import get, static_file, HTTPError

from .projects import static_paths
from .. import settings


@get("/<path:re:.*\\" + settings.document_extension + ">")
def serve_static(path):
    """Serve disseminate files (default: .dm) as plain text files."""
    search_paths = static_paths()

    for search_path in search_paths:
        response = static_file(path, root=search_path, mimetype='text/plain')
        if not isinstance(response, HTTPError):
            return response
    return response


@get("/<path:path>")
def serve_static(path):
    # Retrieve the list of paths to search for static files
    search_paths = static_paths()

    for search_path in search_paths:
        response = static_file(path, root=search_path)
        if not isinstance(response, HTTPError):
            return response
    return response
