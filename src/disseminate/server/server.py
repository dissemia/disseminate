"""
Setup the server
"""
import os
import pathlib
import logging

from flask import Flask

from .views import editor, static_asset
from .. import settings


def get_secret_key():
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


def create_app(in_directory='.', out_directory='.'):
    # Setup the Flask app
    app = Flask('disseminate', instance_relative_config=True)

    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=get_secret_key(),
        in_directory=in_directory,
        out_directory=out_directory
    )

    # Add blueprints
    app.register_blueprint(editor, url='/')
    app.register_blueprint(static_asset, url='/')

    return app


def run_server(in_directory='.', out_directory='.', port=settings.default_port,
               debug=False):
    app = create_app(in_directory, out_directory)
    app.run(host="0.0.0.0", port=port, debug=debug)
