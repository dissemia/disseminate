"""
The 'setup' CLI sub-command.
"""
import click

from .checkers import print_checkers
from .processors import print_processors
from ...tags.processors import ProcessTag
from ...label_manager.processors import ProcessLabels
from ...document.processors import ProcessContext


@click.command()
@click.option('--check', default=False, is_flag=True,
              help='Check required executables and packages')
@click.option('--list-tag-processors', default=False, is_flag=True,
              help='List the available tag processors')
@click.option('--list-label-manager-processors', default=False, is_flag=True,
              help='List the available tag processors')
@click.option('--list-context-processors', default=False, is_flag=True,
              help='List the available context processors')
def setup(check, list_tag_processors, list_label_manager_processors,
          list_context_processors):
    """Setup and configuration options"""
    if check:
        print_checkers()
    elif list_tag_processors:
        print_processors(ProcessTag)
    elif list_label_manager_processors:
        print_processors(ProcessLabels)
    elif list_context_processors:
        print_processors(ProcessContext)
