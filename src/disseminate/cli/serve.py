"""
The 'serve' CLI sub-command for running a webserver.
"""
import click

from .options import file_options, debug_option
from ..server import run_server
from .. import settings


@click.command()
@file_options
@click.option('--port', '-p', default=settings.default_port, show_default=True,
              help="The port to listen to for the webserver")
@debug_option
def serve(in_dir, out_dir, port, debug):
    """Serve documents with a local webserver"""
    run_server(in_directory=in_dir, out_directory=out_dir, port=port,
               debug=debug)
