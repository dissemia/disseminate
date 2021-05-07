"""
The Tornado main app
"""

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options

from .urls import url_patterns
from .handlers.server import server_template_path, ServerHandler
from .. import settings


class TornadoApp(tornado.web.Application):
    def __init__(self, **kwargs):
        tornado.web.Application.__init__(self, url_patterns, **kwargs)


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
    app = TornadoApp(in_path=in_path, out_dir=out_dir, debug=debug,
                     template_path=server_template_path,
                     default_handler_class=ServerHandler)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
