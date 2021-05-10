"""
Tornado unit tests for the handlers
"""
import shutil, tempfile
from pathlib import Path

from tornado.testing import AsyncHTTPTestCase

from disseminate.server.app import get_app
from disseminate.server.store import store


class HandlerTestCase(AsyncHTTPTestCase):
    """A unit testcase for Tornado handlers"""

    def setUp(self):
        # Setup the source directory
        self.in_path = str(Path('.') / 'tests' / 'document' / 'examples' /
                           'ex7')

        # Create temp directories
        self.test_dir = tempfile.mkdtemp()
        self.out_dir = self.test_dir
        super().setUp()

    def tearDown(self):
        # Remove temp directory
        shutil.rmtree(self.test_dir)
        super().tearDown()

    def get_app(self):
        # Create temporary input/output directories
        return get_app(in_path=self.in_path, out_dir=self.out_dir)

    def load_example(self, example_path, create_temp=False):
        """Create a temporary copy of an example directory"""
        # See if a copy of the example is needed
        if create_temp:
            shutil.copytree(example_path, self.test_dir)
            self.in_path = self.test_dir
        else:
            self.in_path = example_path

        # Reset the loaded documents
        if 'root_documents' in store:
            del store['store_documents']

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
        url = '/tests/document/examples/ex7/html/file1.html'

        # Fetch the response for the url
        response = self.fetch(url, raise_error=True)  # Status code 200
        body = response.body.decode('utf-8')  # decode binary

        # Check the page
        assert response.code == 200
        assert '<p>file1.dm</p>' in body
