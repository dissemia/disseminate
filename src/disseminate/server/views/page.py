"""
A view to render pages.
"""
import pathlib

from sanic import response
from sanic.exceptions import abort

from .blueprints import page
from ..projects import load_projects


@page.route('/<path:path>.html')
def render_page(request, path):
    """Render a page"""
    # Reload the project
    root_docs = load_projects(request)

    # Serve the page directly
    path = pathlib.Path(path).with_suffix('.html')
    if path.is_file():
        return response.file(path)

    # Serve the page by reconstructing the path from the target roots
    for root_doc in root_docs:
        target_root = root_doc.target_root
        target_path = target_root / path

        if target_path.is_file():
            return response.file(target_path)

    # Not Found!
    abort(404)
