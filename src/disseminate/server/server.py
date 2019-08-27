"""
Setup the server
"""
import secrets

from sanic import Sanic
from sanic.response import text
from sanic.exceptions import NotFound

from .views.blueprints import system, tree, page, server_static_path
from .views.exceptions import handle_500, handle_404
from .. import settings


def create_secret_key():
    """Create a temporary secret key for sessions"""
    return secrets.token_urlsafe(16)


def create_app(in_path, out_dir=None, debug=False):
    """Create and configure a the app.

    Parameters
    ----------
    in_path : str
        The filenames or path for project root documents.
    out_dir : Optional[str]
        The target root directory to render files to.
    debug : Optional[bool]
        If true, include debugging information.
    """
    # Setup the app
    app = Sanic()

    # Configure the app
    app.debug = debug

    app.config['out_dir'] = out_dir
    app.config['in_path'] = in_path
    app.config['SECRET_KEY'] = create_secret_key()

    # Add blueprints
    app.blueprint(tree)
    app.blueprint(system)
    app.blueprint(page)

    # Add error handlers
    app.error_handler.add(NotFound, handle_404)
    app.error_handler.add(Exception, handle_500)

    # Add the the cwd for static files
    app.static('/favicon.ico', str(server_static_path / 'favicon.ico'))
    app.static('/media', str(server_static_path))
    app.static('/', './', pattern="/?.+\.tex", content_type='text/plain')
    app.static('/', './')

    return app


def run_server(in_path, out_dir, port=settings.default_port,
               debug=False):
    """Create and run the web-server.

    Parameters
    ----------
    in_path : str
        The filenames for project root documents.
    out_dir : str
        The target root directory to render files to.
    port : Optional[int]
        The network port to serve the web-server.
    debug : Optional[bool]
        If true, include debugging information.
    """
    app = create_app(in_path, out_dir, debug)
    app.run(host="127.0.0.1", port=port, debug=debug)
