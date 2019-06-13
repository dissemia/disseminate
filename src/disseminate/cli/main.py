"""
The main disseminate program.
"""
import click
import logging

from .options import debug_option

from ..__version__ import __version__


@click.group()
@click.version_option(__version__, message='v%(version)s')
@debug_option
def main(debug):
    """Disseminate Document Processor"""
    if debug:
        logging.basicConfig(format='%(levelname)-9s:  %(message)s',
                            level=logging.DEBUG)
