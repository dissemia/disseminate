"""
Blueprints for rendering views.
"""

from pathlib import Path

from sanic import Blueprint

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
template_path = Path(__file__).parent.parent.parent / 'templates' / 'server'
static_path = template_path / 'media'

#: Blueprint for tree view
tree = Blueprint('tree', url_prefix='/')

#: Blueprint for system tools
system = Blueprint('system', url_prefix='/system')
