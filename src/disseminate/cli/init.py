"""
The 'init' CLI sub-command.
"""
import click


@click.command()
def init():
    """Initialize a new template project"""
    exc = click.ClickException("Not Implemented")
    exc.exit_code = 1
    raise exc

