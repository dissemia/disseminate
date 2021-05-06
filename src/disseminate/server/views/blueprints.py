"""
Blueprints for rendering views.
"""

from pathlib import Path

from flask import Blueprint

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
server_template_path = (Path(__file__).parent.parent.parent / 'templates' /
                        'server')
server_static_path = server_template_path / 'media'

#: Blueprint for tree view
tree = Blueprint('tree', __name__, url_prefix='/',
                 template_folder=str(server_template_path / 'tree'),
                 static_url_path='/media',
                 static_folder=str(server_static_path))

#: Blueprint for system tools
system = Blueprint('system', __name__, url_prefix='/system',
                   static_url_path='/media',
                   static_folder=str(server_static_path))

#: Blueprint for pages
page = Blueprint('page', __name__, url_prefix='/',
                 template_folder=str(server_template_path))
