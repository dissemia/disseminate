"""
The localhost http server for managing trees and documents.
"""
import http.server
import os.path
import logging

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

        # The root path is special because it renders the tree
        if self.path == "/":
            self.tree.render()
            template = get_template(src_filepath="",
                                    template_basename="tree",
                                    target=".html",
                                    module_only=True)
            html = template.render(body=self.tree.html())

            self.send_response(200)
            self.send_header(b"Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # strip the path of a leading '/', if needed
        path = self.path if not self.path.startswith('/') else self.path[1:]

        # See if it exists in the project_root
        project_path = os.path.join(self.tree.project_root, path)
        print("project_path:", project_path)
        if os.path.isfile(project_path):
            self.path = project_path
            super(RequestHandler, self).do_GET()

        # See if it exists in the target_root
        if self.tree.segregate_targets:
            target_path = None

            # Strip the '.' from the target
            target_list = [t.strip('.') for t in self.tree.target_list]

            for target in target_list:
                test_path = os.path.join(self.tree.target_root, target,
                                         path)
                if os.path.isfile(test_path):
                    target_path = test_path
                    break
        else:
            target_path = os.path.join(self.tree.target_root, path)
            target_path = target_path if os.path.isfile(target_path) else None
        print("target_path:", target_path)
        if target_path:
            self.path = target_path
            super(RequestHandler, self).do_GET()


        # # Point the following requests to the source file path
        # elif path_ext in settings.document_extension:
        #     path = self.path if not self.path.startswith('/') else self.path[1:]
        #
        #     # Switch the path to the source project directory
        #     self.path = os.path.join(self.in_dir, path)
        #     super(RequestHandler, self).do_GET()
        #     return
        #
        # # Point the following requests to the target file paths
        # elif os.path.splitext(self.path)[1] in self.target_list:
        #     # Get the target and path without leading '/' or './
        #     target = os.path.splitext(self.path)[1].strip('.')
        #     path = self.path if not self.path.startswith('/') else self.path[1:]
        #
        #     # Render the tree
        #     self.tree.render()
        #
        #     # Switch the path to the root of the target
        #     if self.tree.segregate_targets:
        #         self.path = os.path.join(self.out_dir, target, path)
        #     else:
        #         self.path = os.path.join(self.out_dir, path)
        #
        super(RequestHandler, self).do_GET()


def run(in_directory, out_directory,
        server_class=http.server.HTTPServer, handler_class=RequestHandler,
        port=settings.default_port):
    # Setup the index tree
    tree1 = Tree(project_root=in_directory, target_root=out_directory,
                 target_list=settings.default_target_list)
    tree1.render()

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
        MyHandler.extensions_map[ext] = "text/plain"

    server_address = ('', port)
    httpd = server_class(server_address, MyHandler)

    try:
        logging.info("Disseminate serving requests on "
                     "port {}...".format(port))
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server.")
        httpd.socket.close()
