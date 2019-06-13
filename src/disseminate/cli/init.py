"""
The 'init' CLI sub-command.
"""
from click import ClickException

from .main import main


@main.command()
def init():
    """Initialize a new template project"""
    exc = ClickException("Not Implemented")
    exc.exit_code = 1
    raise exc

