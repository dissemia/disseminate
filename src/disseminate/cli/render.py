"""
The 'render' CLI sub-command.
"""
import logging

import click

from .options import file_options
from ..document import Document


@click.command()
@file_options
def render(project_filenames, out_dir=None):
    """Render a disseminate project"""
    docs = [Document(src_filepath=project_filename, target_root=out_dir)
            for project_filename in project_filenames]

    for doc in docs:
        logging.info("Rendering document '{}'".format(doc.src_filepath))
        doc.render()
