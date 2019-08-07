"""
Common file options for CLI sub-commands.
"""
import click

debug_option = click.option('--debug', default=False, is_flag=True,
                            help="Show debugging information")


# Project path options

_file_options = [
    click.argument('project_filenames', required=True, nargs=-1,
                   type=click.Path(exists=True)),
    click.option('--out-dir', '-o', required=False,
                 type=click.Path(exists=True, file_okay=False, dir_okay=True),
                 help=("the target directory for the generated output "
                       "documents"))
]


def file_options(func):
    """Wrap the file options in a decorator"""
    for option in reversed(_file_options):
        func = option(func)
    return func
