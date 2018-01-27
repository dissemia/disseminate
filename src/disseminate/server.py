"""
The localhost http server for managing trees and documents.
"""
import http.server
import os.path

from disseminate import __path__
from .tree import Tree
from .templates import get_template
from . import settings


index_html = """<html>
<head>
  <title>Index</title>
</head>
<body>
{}
</body>
</html>
"""


class RequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
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
        elif os.path.exists(os.path.join(self.module_path, self.path[1:])):
            self.path = os.path.join(self.module_path, self.path[1:])
            print(self.path)
            super(RequestHandler, self).do_GET()
        else:
            super(RequestHandler, self).do_GET()

    # def translate_path(self, path):
    #     # Remove the prefix forward slash, if present
    #     path = path[1:] if path.startswith("/") else path
    #
    #     # Create a new path for the target project directory
    #     path = os.path.join(self.subdirectory, path)
    #     print(path)
    #     return super(RequestHandler, self).translate_path(path)


def run(in_dir, out_dir,
        server_class=http.server.HTTPServer, handler_class=RequestHandler):
    # Setup the tree
    tree1 = Tree(subpath=in_dir, output_dir=out_dir)
    tree1.find_documents()



    class MyHandler(handler_class):
        tree = tree1
        subdirectory = tree1.project_root()
        # Setup the module path to serve css files
        module_path = os.path.relpath(os.path.join(__path__[0], "templates"),
                                      os.path.curdir)

    MyHandler.extensions_map[settings.document_extension] = "text/plain"

    server_address = ('', settings.default_port)
    httpd = server_class(server_address, MyHandler)
    httpd.serve_forever()
