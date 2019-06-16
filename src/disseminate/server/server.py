"""
Setup the server
"""
import os
import pathlib
import logging

from flask import Flask

try:
    from flask_debugtoolbar import DebugToolbarExtension
except ImportError:
    DebugToolbarExtension = None

from .views.blueprints import editor, static_asset
from .views.handlers import page_not_found
from .projects import load_projects
from .. import settings


def get_secret_key():
    """Load or generate a secret key for server sessions.

    Returns
    -------
    secret : bytes
        The loaded or generated secret string.
    """
    secret_path = pathlib.Path(__file__).parent / 'secret.txt'

    if secret_path.is_file():
        return secret_path.read_bytes()

    # Generate a new secret, and try saving it to a file
    secret = os.urandom(16)
    try:
        secret_path.write_bytes(secret)
    except PermissionError:
        msg = ("Could not write secret to file for server. The temporary "
               "secret '{}' was used.".format(secret))
        logging.error(msg)
    return secret


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

    app.config['SECRET_KEY'] = get_secret_key()
    app.config['out_dir'] = out_dir
    app.config['project_filenames'] = project_filenames

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
    app.run(host="0.0.0.0", port=port, debug=debug)
