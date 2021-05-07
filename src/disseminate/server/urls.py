"""
URL routes for the Tornado server
"""
import mimetypes

from tornado.web import url, StaticFileHandler

from .handlers import (TreeHandler, CheckerHandler, SignalHandler,
                       CustomStaticFileHandler, PygmentizeHandler,
                       server_static_path)


url_patterns = [
    url(r"/", TreeHandler, name="tree"),
    url(r"/checkers", CheckerHandler, name="checkers"),
    url(r"/signals", SignalHandler, name="signals"),
    url(r"/media/(.*)", CustomStaticFileHandler, {'path': server_static_path}),
    url(r"/(.*\.dm)", PygmentizeHandler, name='disseminate_source'),
    url(r"/(.*\.tex)", PygmentizeHandler, name='latex_source'),
    url(r"/(.*)", CustomStaticFileHandler, {'path': '.'}),
]
