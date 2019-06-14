"""
The 'render' CLI sub-command.
"""
import click


@click.command()
def render():
    """Render a disseminate project"""
    exc = click.ClickException("Not Implemented")
    exc.exit_code = 1
    raise exc
