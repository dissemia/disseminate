"""
Setup the server
"""
import secrets

from flask import Flask

try:
    from flask_debugtoolbar import DebugToolbarExtension
except ImportError:
    DebugToolbarExtension = None

from .views.blueprints import editor, static_asset
from .views.handlers import page_not_found
from .projects import load_projects
from .. import settings


def create_secret_key():
    """Create a temporary secret key for sessions"""
    return secrets.token_urlsafe(16)


def create_app(project_filenames, out_dir=None, debug=False):
    """Create and configure a flask app.

    Parameters
    ----------
    project_filenames : Tuple[str]
        The filenames for project root documents.
    out_dir : Optional[str]
        The target root directory to render files to.
    debug : Optional[bool]
        If true, include debugging information.
    """
    # Setup the Flask app
    app = Flask('disseminate', instance_relative_config=True)

    # Configure the app
    app.debug = debug

    app.config['out_dir'] = out_dir
    app.config['project_filenames'] = project_filenames
    app.config['SECRET_KEY'] = create_secret_key()

    # Add blueprints
    app.register_blueprint(editor, url='/')
    app.register_blueprint(static_asset, url='/')
    app.register_error_handler(404, page_not_found)

    # Wrap extensions
    if DebugToolbarExtension is not None:
        toolbar = DebugToolbarExtension(app)

    # Load the documents and projects
    with app.app_context():
        load_projects()

    return app


def run_server(project_filenames, out_dir='.', port=settings.default_port,
               debug=False):
    """Create and run the web-server.

    Parameters
    ----------
    project_filenames : Tuple[str]
        The filenames for project root documents.
    out_dir : Optional[str]
        The target root directory to render files to.
    port : Optional[int]
        The network port to serve the web-server.
    debug : Optional[bool]
        If true, include debugging information.
    """
    app = create_app(project_filenames, out_dir, debug)
    app.run(host="127.0.0.1", port=port, debug=debug)
