"""
The 'preview' subcommand.
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
def preview(project_filenames, out_dir, port, debug):
    """Preview documents with a local webserver"""
    run_server(project_filenames=project_filenames, out_dir=out_dir, port=port,
               debug=debug)
