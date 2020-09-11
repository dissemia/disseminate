"""
The main disseminate program.
"""
import click
import logging

from .options import debug_option
from .init import init
from .build import build
from .preview import preview
from .setup import setup

from ..__version__ import __version__


@click.group()
@click.version_option(__version__, message='v%(version)s')
@debug_option
def main(debug):
    """Disseminate Document Processor"""
    if debug:
        logging.basicConfig(format='%(levelname)-9s:  %(message)s',
                            level=logging.DEBUG)


main.add_command(init)
main.add_command(build)
main.add_command(preview)
main.add_command(setup)
