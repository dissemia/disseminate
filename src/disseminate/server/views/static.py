"""
Functions for serving static files.
"""
import pathlib

from flask import send_from_directory

from .blueprints import static_asset


current_directory = pathlib.Path('.').absolute()


@static_asset.route('/<path:path>.html')
def serve_static_html(path):
    """View to serve rendered html files."""
    return send_from_directory(directory=current_directory,
                               filename=path + '.html')


@static_asset.route('/<path:path>')
def serve_static(path):
    """View to serve static files."""
    return send_from_directory(directory=current_directory,
                               filename=path)
