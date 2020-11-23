"""
The 'render' CLI sub-command.

.. note:: Implementing a progressbar using click or tqdm sometimes crashes
          the program without an exception and has crashed the terminal. I
          suspect it has to do with the redraw implementation. For this reason,
          these tools aren't used for the progress bar.
"""
import click

from .options import file_options, check_out_dir
from .utils.progressbar import ProgressTable
from ..builders.environment import Environment


@click.command()
@file_options
@click.option('-p', '--progress', is_flag=True, default=False,
              help="Show a progress bar for the build")
def build(in_path, out_dir=None, progress=False):
    """Build a disseminate project"""
    # Setup the build environment
    envs = Environment.create_environments(root_path=in_path,
                                           target_root=out_dir)
    docs = [env.root_document for env in envs]
    check_out_dir(root_docs=docs, out_dir=out_dir)

    for env in envs:
        root_builder = env.create_root_builder()
        builders = root_builder.flatten()

        if progress:  # Print progress, if enabled
            progress_table = ProgressTable(environment=env)
            progress_table.print_hdr()
            progress_table.print_row(builders)

        status = root_builder.status
        while status in {'ready', 'building'}:
            status = root_builder.build(complete=False)

            if progress:  # Print progress, if enabled
                progress_table.print_row(builders)
        print('Build:', root_builder.status)
