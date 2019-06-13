"""
The 'render' CLI sub-command.
"""
from click import ClickException

from .main import main


@main.command()
def render():
    """Render a disseminate project"""
    exc = ClickException("Not Implemented")
    exc.exit_code = 1
    raise exc
