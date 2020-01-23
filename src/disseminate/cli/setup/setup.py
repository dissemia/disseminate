"""
The 'setup' CLI sub-command.
"""
import click

from .checkers import print_checkers
from .signals import print_signals
from ...signals.signals import signals


@click.command()
@click.option('--check', default=False, is_flag=True,
              help='Check required executables and packages')
@click.option('--list-signals', default=False, is_flag=True,
              help='List the available signals')
def setup(check, list_signals):
    """Setup and configuration options"""
    if check:
        print_checkers()
    elif list_signals:
        print_signals(signals)
