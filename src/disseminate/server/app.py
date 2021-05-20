"""
The Tornado main app
"""

import tornado.httpserver
import tornado.ioloop
import tornado.web

from .urls import url_patterns
from .handlers.server import server_template_path, ServerHandler
from .. import settings


class TornadoApp(tornado.web.Application):
    """The Tornado App for the built-in webserver"""
    def __init__(self, **kwargs):
        tornado.web.Application.__init__(self, url_patterns, **kwargs)


def get_app(in_path, out_dir, debug=False, **kwargs):
    """Create the Tornado app instance"""
    app = TornadoApp(in_path=in_path, out_dir=out_dir, debug=debug,
                     template_path=server_template_path,
                     default_handler_class=ServerHandler)
    return app


def run_server(in_path, out_dir, port=settings.default_port,
               debug=False):
    """Create and run the web-server.

    Parameters
    ----------
    in_path : str
        The filenames for project root documents.
    out_dir : str
        The target root directory to render files to.
    port : Optional[int]
        The network port to serve the web-server.
    debug : Optional[bool]
        If true, include debugging information.
    """
    app = get_app(in_path=in_path, out_dir=out_dir, debug=debug)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port, '127.0.0.1')  # listen only to the localhost
    tornado.ioloop.IOLoop.instance().start()
