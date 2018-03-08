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
from .tree import Tree
from .templates import get_template
from . import settings


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """A specialized request handler to serve index trees, files from the
    package or files from the document (source markup) directories."""

    def do_GET(self):
        # cut off a query string
        if '?' in self.path:
            self.path, _ = self.path.split('?', 1)

        # Parse the self.path
        path_ext = os.path.splitext(self.path)[1]

        # Try the render if it's a request for a file that is in this tree's
        # target list. If it's unsuccessful, handle the exception
        if path_ext in self.tree.target_list:
            try:
                if __debug__: # timing information for debug
                    t0 = time.time()

                self.tree.render()

                if __debug__:
                    t1 = time.time()
                    msg = "Render time: {:.1f} ms".format(1000. * (t1-t0))
                    logging.debug(msg)
            except Exception as e:
                # Get the exception template
                template = get_template(src_filepath="",
                                        template_basename="exception",
                                        target=".html",
                                        module_only=True)

                # format the context and traceback
                # TODO: Move the description away from the __doc__ attribute,
                # since this can be stripped by python optimizations
                tb = ''.join(format_exception(type(e), e, e.__traceback__))
                context = {'name': e.__class__.__name__,
                           'description': e.__class__.__doc__,
                           'traceback': tb,
                           'exception': e}

                # render the html and respond
                html = template.render(**context)
                self.send_response(500)
                self.send_header(b"Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))

                return

        # The root path is special because it renders the tree
        if self.path == "/":
            template = get_template(src_filepath="",
                                    template_basename="tree",
                                    target=".html",
                                    module_only=True)
            html = template.render(body=self.tree.html())

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

        # strip the path of a leading '/', if needed
        stripped_path = path if not path.startswith('/') else path[1:]

        # cut off a query string
        if '?' in stripped_path:
            stripped_path, _ = stripped_path.split('?', 1)

        # See if it exists in the project_root
        project_path = os.path.join(self.tree.project_root, stripped_path)
        if os.path.isfile(project_path):
            return project_path

        # See if it exists in the target_root
        if self.tree.segregate_targets:
            # Strip the '.' from the target
            target_list = [t.strip('.') for t in self.tree.target_list]

            for target in target_list:
                test_path = os.path.join(self.tree.target_root, target,
                                         stripped_path)
                if os.path.isfile(test_path):
                    return test_path
        else:
            return os.path.join(self.tree.target_root, stripped_path)
        return path


def run(in_directory, out_directory,
        server_class=http.server.HTTPServer, handler_class=RequestHandler,
        port=settings.default_port):
    # Setup the index tree
    tree1 = Tree(project_root=in_directory, target_root=out_directory,
                 target_list=settings.default_target_list)
    tree1.find_documents()

    # Customize the request handler with the tree
    class MyHandler(handler_class):
        in_dir = in_directory
        out_dir = out_directory
        tree = tree1
        target_list = tree1.target_list

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
