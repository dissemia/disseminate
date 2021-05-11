"""
URL routes for the Tornado server
"""
from tornado.web import url

from .handlers import (TreeHandler, CheckerHandler, SignalHandler,
                       CustomStaticFileHandler, PygmentizeHandler,
                       server_static_path)


url_patterns = [
    url(r"/", TreeHandler, name="tree"),
    url(r"/checkers", CheckerHandler, name="checkers"),
    url(r"/signals", SignalHandler, name="signals"),
    url(r"/media/(.*)", CustomStaticFileHandler, {'path': server_static_path}),
    url(r"/(.*\.dm)", PygmentizeHandler, name='disseminate_source'),
    url(r"/(.*\.tex)", PygmentizeHandler, name='latex_source',
        kwargs={'reload_projects': True}),
    url(r"/(.*\.html)", CustomStaticFileHandler,
        kwargs={'path': '.', 'reload_projects': True}),
    url(r"/(.*\.epub)", CustomStaticFileHandler,
        kwargs={'path': '.', 'reload_projects': True}),
    url(r"/(.*)", CustomStaticFileHandler, {'path': '.'}),
]
