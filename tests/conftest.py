import copy
import pytest
import io

from disseminate.context import BaseContext


@pytest.fixture
def context_cls():
    """Returns a copy of the context class."""
    CopyContext = copy.deepcopy(BaseContext)
    return CopyContext


@pytest.fixture
def url_request(monkeypatch):
    """Mock requests to url.requests so that responses inserted in the
    self.responses dict are returned instead of polling the internet."""

    class MockRequest(object):
        responses = None

        def __init__(self):
            self.responses = dict()

        def urlopen(self, url):
            # Get the url response
            response = self.responses[url]

            # Convert to a text stream
            return io.BytesIO(response.encode())

    import urllib
    mockrequest = MockRequest()
    monkeypatch.setattr(urllib, 'request', mockrequest)

    return mockrequest


@pytest.fixture
def a_in_b():
    """Test whether items in 'a' are in 'b'."""
    def _a_in_b(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            return (all(k in b for k in a.keys()) and
                    all(a[k] == b[k] for k in a.keys()))
        return False

    return _a_in_b
