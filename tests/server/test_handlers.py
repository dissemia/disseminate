"""
Tornado unit tests for the handlers
"""
import shutil
import tempfile
import os
from distutils.dir_util import copy_tree
from pathlib import Path

from tornado.testing import AsyncHTTPTestCase

from disseminate.server.app import get_app
from disseminate.server.handlers.store import reset_store

# Example path
ex4 = Path('.') / 'tests' / 'document' / 'examples' / 'ex4'
ex7 = Path('.') / 'tests' / 'document' / 'examples' / 'ex7'


class HandlerTestCase(AsyncHTTPTestCase):
    """A unit testcase for Tornado handlers"""

    def setUp(self):
        # Get the current working directory
        self.cwd = os.getcwd()

        # Setup the source directory
        self.in_path = str(ex7)

        # Create temp directories
        self.temp_dir = tempfile.mkdtemp()
        self.out_dir = self.temp_dir

        # Change to the temp directory
        os.chdir(self.temp_dir)

        super().setUp()

    def tearDown(self):
        # Remove temp directory
        shutil.rmtree(self.temp_dir)

        # Reset the current working directory
        os.chdir(self.cwd)

        super().tearDown()

    def get_app(self):
        # Create temporary input/output directories
        app = get_app(in_path=self.in_path, out_dir=self.out_dir)

        # Load a temporary copy of example 7
        self.load_example(example_path=ex7, create_temp=True)

        # Change the app path to the example directory
        self.set_app_paths(app=app, in_path=self.in_path, out_dir=self.in_path)

        return app

    def load_example(self, example_path, create_temp=False):
        """Create a temporary copy of an example directory"""
        example_path = Path(example_path)

        # Translate the example_path to the test directory's cwd if needed
        if not example_path.is_dir():
            example_path = Path(self.cwd) / example_path

        # See if a copy of the example is needed
        if create_temp:
            in_path = str(Path(self.temp_dir) / example_path.name)
            copy_tree(str(example_path), in_path)
            self.in_path = in_path
        else:
            self.in_path = str(example_path)

        # Reset the loaded documents in the store
        reset_store()

    def set_app_paths(self, app, in_path=None, out_dir=None, chdir=True):
        """Set the paths for the Tornado app"""
        # Set the app paths
        if in_path is not None:
            app.settings['in_path'] = str(in_path)
        if out_dir is not None:
            app.settings['out_dir'] = str(out_dir)
        if chdir:
            os.chdir(str(in_path))

    def test_tree_handler(self):
        """Tests for the tree handler"""
        # Get the tree handler url
        app = self.get_app()
        url = app.reverse_url('tree')

        # Fetch the response for the url
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary

        # The client loads 'tests/document/examples/ex7'
        # tests/document/examples/ex7
        # └── src
        #     ├── file1.dm
        #     └── sub1
        #         ├── file11.dm
        #         └── subsub1
        #             └── file111.dm
        assert response.code == 200
        assert 'source' in body
        assert 'file1.dm' in body
        assert 'sub1/file11.dm' in body
        assert 'sub1/subsub1/file111.dm' in body

    # def test_tree_handler_multiple_project(self):
    #     """Test the tree handler with multiple projects"""
    #     # Load and create temporary copies of multiple projects. By default,
    #     # ex7 is copied for all tests so ex4 is loaded as well.
    #     self.load_example(ex4, create_temp=True)
    #     self.load_example(ex7, create_temp=True)
    #
    #     # Switch the current directory to the root temp dir to include both
    #     # projects
    #     app = self.get_app()
    #     in_path = Path(self.in_path).parent
    #     self.set_app_paths(app=app, in_path=in_path, chdir=True)
    #
    #     # Try loading the tree
    #     url = app.reverse_url('tree')
    #
    #     # Fetch the response for the url
    #     response = self.fetch(url, raise_error=True)  # Status code 200
    #     body = response.body.decode('utf-8')  # decode binary
    #
    #     assert response.code == 404

    def test_checkers_handler(self):
        """Tests for the checkers handler"""
        # Get the checkers handler url
        app = self.get_app()
        url = app.reverse_url('checkers')

        # Fetch the response for the url
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary

        # Check the page
        assert response.code == 200
        assert 'Checking required dependencies' in body
        assert 'python' in body  # Python dependency checked
        assert 'ok' in body  # At least an ok for python dependency

    def test_signals_handler(self):
        """Tests for the signals handler"""
        # Get the checkers handler url
        app = self.get_app()
        url = app.reverse_url('signals')

        # Fetch the response for the url
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary

        # Check the page
        assert response.code == 200
        assert 'Signals Listing' in body

    def test_error_404(self):
        """Test the 404 error page"""
        # Fetch missing url
        url = '/missing.html'
        response = self.fetch(url)
        body = response.body.decode('utf-8')  # decode binary

        # Check the rendered page to make sure it's a custom page
        assert response.code == 404
        assert 'File not Found!' in body
        assert 'Disseminate' in body

    def test_project_page_handler(self):
        """Test for the loading of a project page"""
        # Get the url
        url = '/html/file1.html'

        # Fetch the response for the url.
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary

        # Check the page
        assert response.code == 200
        assert '<p>file1.dm</p>' in body

    def test_project_reload(self):
        """Test the rebuilding of project pages on change"""
        # Check the tree listing
        app = self.get_app()
        tree_url = app.reverse_url('tree')
        response = self.fetch(tree_url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary
        assert response.code == 200
        assert 'file1.dm' in body
        assert 'sub1/file11.dm' in body
        assert 'sub1/subsub1/file111.dm' in body

        # Check that the root document was compiled (file1.dm)
        url = '/html/file1.html'
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary
        assert response.code == 200
        assert 'Updated file' not in body
        assert '<p>file1.dm</p>' in body

        # Change the file and see if if the project is updated.
        root_doc = Path(self.in_path) / 'src' / 'file1.dm'
        root_doc.write_text("""
        Updated file
        """)

        # The tree now only includes the root doc. The tree is updated.
        response = self.fetch(tree_url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary
        assert response.code == 200
        assert 'file1.dm' in body
        assert 'sub1/file11.dm' not in body
        assert 'sub1/subsub1/file111.dm' not in body

        # The root document has been updated
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary
        assert response.code == 200
        assert 'Updated file' in body
