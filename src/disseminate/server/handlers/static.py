"""
Static file handlers
"""
from tornado.web import StaticFileHandler

from .server import ServerHandler


class CustomStaticFileHandler(ServerHandler, StaticFileHandler):
    """A custom static file handler that handles rendered error pages"""
    pass
