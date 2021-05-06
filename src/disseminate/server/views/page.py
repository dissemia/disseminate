"""
A view to render pages.
"""
import pathlib

from flask import send_file, render_template
from werkzeug.exceptions import abort

from .blueprints import page
from ..projects import load_projects


@page.route('/<path:path>')
def render_page(path):
    """Render a page"""
    # Reload the project
    root_docs = load_projects()

    # Serve the page directly
    path = pathlib.Path(path)
    if path.is_file():
        return send_file(path)

    # Serve the page by reconstructing the path from the target roots
    for root_doc in root_docs:
        target_root = root_doc.target_root
        target_path = target_root / path

        if target_path.is_file():
            return send_file(target_path)

    # Not Found!
    abort(404)
