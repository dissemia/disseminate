"""
The 'render' CLI sub-command.
"""
import logging

import click

from .options import file_options
from ..document.utils import load_root_documents


@click.command()
@file_options
def render(in_path, out_dir):
    """Render a disseminate project"""
    docs = load_root_documents(path=in_path, target_root=out_dir)

    for doc in docs:
        logging.info("Rendering document '{}'".format(doc.src_filepath))
        doc.render()
