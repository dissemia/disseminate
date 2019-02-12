"""
The main disseminate program.
"""

import logging
import argparse
import os.path

from .server import run
from . import settings


def is_directory(value):
    is_dir = os.path.isdir(value)
    if not is_dir and value == 'src':
        value = '.'
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError("'{}' is not a directory. The input "
                                         "and output must be "
                                         "directories".format(value))
    return value


def format_ext(value):
    """Format the target extensions list."""
    return '.' + value if not value.startswith('.') else value


# TODO: add clean or clear option to remove targets and .cache
def main():
    """The main command-line interface (CLI) for rendering disseminate
    documents."""
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

    # Arguments to main parser
    parser.add_argument('--debug', action='store_true',
                        help='print debug messages to stderr')

    # Arguments common to sub-parsers
    for p in (render, serve):
        p.add_argument('-i',
                       action='store', default='src',
                       type=is_directory,
                       help="the project root directory for the input source "
                            "files")
        p.add_argument('-o',
                       action='store', default='.',
                       type=is_directory,
                       help="the target root directory for the generated "
                            "output documents")

    # init arguments
    init.add_argument('destination', default='', nargs='?',
                      help="The destination directory to initialize a project "
                           "(default: {})".format("current directory"))

    # serve arguments
    serve.add_argument('-p', '--port',
                       action='store', default=settings.default_port,
                       type=int,
                       help="The port to listen to for the webserver "
                            "(default: {})".format(settings.default_port))

    # Parse the commands
    args = parser.parse_args()
    if args.command not in ('init', 'serve', 'render'):
        parser.print_help()
        exit()

    # Set the default logging level to info
    if args.debug:
        logging.basicConfig(format='%(levelname)-9s:  %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)-9s:  %(message)s',
                        level=logging.INFO)

    # Handle the sub-commands
    # if args.command == 'init':
    #     quickstart(args.destination)

    if args.command == 'render':
        #tree1 = Tree(project_root=args.i, target_root=args.o,
        #             target_list=settings.default_target_list)
        #tree1.render()
        pass

    if args.command == 'serve':
        run(in_directory=args.i, out_directory=args.o, port=args.port)
