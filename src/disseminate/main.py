"""
The main disseminate program.
"""

import logging
import argparse

from .server import run


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='disseminate documents')
    base_parser = parser.add_subparsers(description='processor commands',
                                        dest='command')

    render = base_parser.add_parser('render',
                                    help="render documents")

    serve = base_parser.add_parser('serve',
                                   help="serve documents with a local "
                                        "webserver")
    for p in (render, serve):
        p.add_argument('-i',
                       action='store', default='.',
                       help="the directory for the input source files")
        p.add_argument('-o',
                       action='store', default='.',
                       help="the directory for the generated documents")

    # Parse the commands
    args = parser.parse_args()
    if args.command not in ('serve', 'render'):
        parser.print_help()
        exit()

    if args.command == 'serve':
        run(in_dir=args.i, out_dir=args.o)
