"""
The 'render' CLI sub-command.
"""
import logging

import click

from .options import file_options, check_out_dir
from ..document.utils import load_root_documents


@click.command()
@file_options
def render(in_path, out_dir=None):
    """Render a disseminate project"""
    docs = load_root_documents(path=in_path, target_root=out_dir)

    check_out_dir(root_docs=docs, out_dir=out_dir)

    for doc in docs:
        logging.info("Rendering document '{}'".format(doc.src_filepath))
        doc.render()
