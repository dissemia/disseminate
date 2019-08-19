"""
Blueprints for rendering views.
"""

from pathlib import Path

from sanic import Blueprint

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
server_template_path = (Path(__file__).parent.parent.parent / 'templates' /
                        'server')
server_static_path = server_template_path / 'media'

#: Blueprint for tree view
tree = Blueprint('tree', url_prefix='/')

#: Blueprint for system tools
system = Blueprint('system', url_prefix='/system')

#: Blueprint for pages
page = Blueprint('page', url_prefix='/')
