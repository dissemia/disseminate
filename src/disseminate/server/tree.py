"""
Function to render the project tree.
"""
from pathlib import Path
from os.path import relpath

from bottle import get, jinja2_view, TEMPLATE_PATH

from .projects import load_projects
from ..document.utils import render_tree_html

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
template_path = relpath(Path(__file__).parent.parent / 'templates', '')
TEMPLATE_PATH.append(str(template_path))


@get('/')
@get('/index.html')
@jinja2_view('server/tree.html')
def render_tree():
    # Get the documents
    docs = load_projects()
    return {'body': render_tree_html(docs)}
