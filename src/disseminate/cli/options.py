"""
Common file options for CLI sub-commands.
"""
import click

from ..utils.string import nicejoin

debug_option = click.option('--debug', default=False, is_flag=True,
                            help="Show debugging information")


# Project path options


in_option = click.option('--in-path', '-i', required=False,
                         type=click.Path(exists=True, file_okay=True,
                                         dir_okay=True),
                         default='.',
                         help="the directory or file path for a project root "
                              "document")
out_option = click.option('--out-dir', '-o', required=False,
                          type=click.Path(exists=True, file_okay=False,
                                          dir_okay=True),
                          default=None,
                          help="the target directory for the generated output "
                               "documents")

_file_options = [in_option, out_option]


def file_options(func):
    """Wrap the file options in a decorator"""
    for option in reversed(_file_options):
        func = option(func)
    return func


def check_out_dir(root_docs, out_dir):
    """Check that there is only 1 project when specifying the output directory.

    Multiple projects cannot (currently) write to the same output directory.
    """
    if len(root_docs) > 1 and out_dir is not None:
        docs_string = [repr(d) for d in root_docs]
        msg = ("The '-o' flag only work when one project is specified. "
               "The following projects are currently "
               "loaded: {}".format(nicejoin(*docs_string)))
        raise click.BadParameter(msg)
