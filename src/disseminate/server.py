"""
The localhost http server for managing trees and documents.
"""
import http.server
import os.path
import logging
from traceback import format_exception
if __debug__:
    import time

from disseminate import __path__
from disseminate.document.utils import (load_root_documents, render_tree_html,
                                        translate_path)
from .templates import get_template
from . import settings


def render(documents):
    """Render the given documents"""
    for document in documents:
        if __debug__:  # Timing for debugging
            t0 = time.time()

        document.render()

        if __debug__:
            t1 = time.time()
            print("{} render time {:.1f} ms".format(document,
                                                    1000. * (t1 - t0)))

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """A specialized request handler to serve index trees, files from the
    package or files from the document (source markup) directories."""

    def do_GET(self):
        # cut off a query string
        if '?' in self.path:
            self.path, _ = self.path.split('?', 1)

        # The root path is special because it renders the tree
        if self.path == "/":
            template = get_template(src_filepath="",
                                    template_basename="tree",
                                    target=".html",
                                    module_only=True)
            # html = template.render(body=self.tree.html())
            html = template.render(body=render_tree_html(self.documents))

            self.send_response(200)
            self.send_header(b"Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else:
            super(RequestHandler, self).do_GET()

    def translate_path(self, path):
        # Let do_GET handle root requests
        if path == '/':
            return path

        # cut off a query string
        if '?' in path:
            path, _ = path.split('?', 1)

        # See if any files need to be rendered
        render(self.documents)

        # See if the file is in the targets of one of the documents
        render_path = translate_path(self.path, self.documents)

        # Render the documents and return the render_path
        if render_path is not None:
            render(self.documents)
            return render_path

        return path


def run(in_directory, out_directory,
        server_class=http.server.HTTPServer, handler_class=RequestHandler,
        port=settings.default_port):

    # Fetch the root documents
    docs = load_root_documents(path=in_directory)

    # Render the documents
    render(docs)

    # Customize the request handler with the tree
    class MyHandler(handler_class):
        in_dir = in_directory
        out_dir = out_directory
        documents = docs

        # Setup the module path to serve css files
        module_path = os.path.relpath(os.path.join(__path__[0], "templates"),
                                      os.path.curdir)

    # Serve the following files as plain text files
    for ext in [settings.document_extension, ] + settings.text_extensions:
        MyHandler.extensions_map[ext] = "text/plain; charset=utf-8"

    server_address = ('', port)
    httpd = server_class(server_address, MyHandler)

    try:
        logging.info("Disseminate serving requests on "
                     "port {}...".format(port))
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server.")
        httpd.socket.close()
