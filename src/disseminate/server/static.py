"""
Functions for serving static files.
"""
from bottle import get, static_file

from .. import settings


@get("/<path:re:.*\\" + settings.document_extension + ">")
def serve_static(path):
    """Serve disseminate files (default: .dm) as plain text files."""
    return static_file(path, root='.', mimetype='text/plain')


@get("/<path:path>")
def serve_static(path):
    return static_file(path, root='.')
