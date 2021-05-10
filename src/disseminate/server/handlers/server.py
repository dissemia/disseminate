"""
A generic request handler for server functions.
"""
import platform
from pathlib import Path
from traceback import extract_tb, format_list
from sys import executable as python_executable

from tornado.web import RequestHandler

from .projects import load_projects
from ...__version__ import __version__


# Get the path for the templates directory and add it to the bottle
# TEMPLATE_PATH
server_template_path = (Path(__file__).parent.parent.parent / 'templates' /
                        'server')
server_static_path = server_template_path / 'media'


class ServerHandler(RequestHandler):
    """A request handler for server functions"""

    def initialize(self, reload_projects=False, *args, **kwargs):
        if reload_projects:
            load_projects(self.application)
        super().initialize(*args, **kwargs)

    def set_default_headers(self):
        # Disable mimetype sniffing/guessing to allow viewing of plain/text
        self.set_header('X-Content-Type-Options', 'nosniff')

    def get_template_path(self):
        """The template path for the server templates"""
        return str(server_template_path)

    def write_error(self, status_code, **kwargs):
        """Render custom error pages"""
        # Add information on the current version of the software
        kwargs['version'] = __version__
        kwargs['python_version'] = platform.python_version()
        kwargs['python_executable'] = python_executable

        # Add information on the platform
        kwargs['platform'] = platform.platform()

        # Parse the exception and populate the message kwarg
        exc_info = kwargs.get('exc_info', None)

        if exc_info is not None and len(exc_info) == 3:
            # Unpack exc_info into the exception class, exception instance and
            # traceback
            exc_type, exc, tb = exc_info

            # Parse the exception
            kwargs['exc'] = exc
            kwargs['exc_type'] = exc_type.__name__
            kwargs['exc_filename'] = getattr(exc, 'filename', '')
            kwargs['exc_lineno'] = getattr(exc, 'lineno', '')
            kwargs['exc_msg'] = exc.args[0] if len(exc.args) > 0 else ''
            kwargs['exc_args'] = exc.args
            # Parse the traceback
            kwargs['traceback'] = format_list(extract_tb(tb))

        if status_code == 404:
            self.render("404.html", status_code=status_code, **kwargs)
        elif status_code == 500:
            self.render("500.html", status_code=status_code, **kwargs)
        else:
            self.render("error.html", status_code=status_code, **kwargs)
