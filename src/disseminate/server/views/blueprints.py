from pathlib import Path

from flask import Blueprint

# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
template_path = Path(__file__).parent.parent.parent / 'templates' / 'server'
static_path = template_path / 'media'

#: Blueprint for editor tools
editor = Blueprint('editor_page', __name__,
                   template_folder=template_path,
                   static_folder=static_path,
                   static_url_path='/media')


#: Blueprint for static assets and files
static_asset = Blueprint('static_asset', __name__,
                         static_folder='.',
                         static_url_path='/')
