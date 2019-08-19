"""
A view to render pages.
"""
from sanic import response

from .blueprints import page
from ..projects import load_projects


@page.route('<path:path>.html')
def render_page(request, path):
    """Render a page"""
    # Reload the project
    load_projects(request)

    # Serve the page
    return response.file(path + '.html')
