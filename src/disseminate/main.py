"""
The main disseminate program.
"""

import logging
import argparse
import os.path

from .server import run
from . import settings


def is_directory(value):
    if not os.path.isdir(value):
         raise argparse.ArgumentTypeError("'{}' is not a directory. The input "
                                          "and output must be "
                                          "directories".format(value))
    return value


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='disseminate documents')
    base_parser = parser.add_subparsers(description='processor commands',
                                        dest='command')

    init = base_parser.add_parser('init',
                                  help="Initialize a new project")

    render = base_parser.add_parser('render',
                                    help="render documents")

    serve = base_parser.add_parser('serve',
                                   help="serve documents with a local "
                                        "webserver")

    # Arguments common to sub-parsers
    for p in (render, serve):
        p.add_argument('-i',
                       action='store', default='.',
                       type=is_directory,
                       help="the project root directory for the input source "
                            "files")
        p.add_argument('-o',
                       action='store', default='.',
                       type=is_directory,
                       help="the target root directory for the generated "
                            "output documents")

    # Serve arguments
    serve.add_argument('-p', '--port',
                       action='store', default=settings.default_port,
                       help="The port to listen to for the webserver "
                            "(default: {})".format(settings.default_port))

    # Parse the commands
    args = parser.parse_args()
    if args.command not in ('serve', 'render'):
        parser.print_help()
        exit()

    # Set the default logging level to info
    logging.basicConfig(format='%(levelname)-9s:  %(message)s',
                        level=logging.INFO)

    if args.command == 'serve':
        run(in_directory=args.i, out_directory=args.o)
