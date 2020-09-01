"""
The 'render' CLI sub-command.
"""
import logging

import click

from .options import file_options, check_out_dir
from ..builders.environment import Environment


@click.command()
@file_options
def build(in_path, out_dir=None):
    """Build a disseminate project"""
    envs = Environment.create_environments(root_path=in_path,
                                           target_root=out_dir)
    docs = [env.root_document for env in envs]
    check_out_dir(root_docs=docs, out_dir=out_dir)

    for doc in docs:
        logging.info("Building document '{}'".format(doc.src_filepath))
        doc.build(complete=True)
