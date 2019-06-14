"""
Common file options for CLI sub-commands.
"""
import pathlib

import click

debug_option = click.option('--debug', default=False, is_flag=True,
                            help="Show debugging information")


# Project path options

def is_dir(ctx, param, value):
    """Validate that the given value is a directory."""
    path = pathlib.Path(value)
    if path.is_dir():
        return path
    else:
        raise click.BadParameter("The path for must be a directory")


_file_options = [
    click.option('--in-dir', '-i', default='src', show_default=True,
                 callback=is_dir, type=click.Path(exists=True),
                 help='the project root directory for the input source'),
    click.option('--out-dir', '-o', default='.', show_default=True,
                 callback=is_dir, type=click.Path(exists=True),
                 help=("the target root directory for the generated output "
                       "documents"))
]


def file_options(func):
    """Wrap the file options in a decorator"""
    for option in reversed(_file_options):
        func = option(func)
    return func
