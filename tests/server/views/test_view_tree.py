"""
Test the tree (document list) view.
"""
import os


async def test_view_tree(app, test_client):
    """Test the rendering of the checkers view."""
    # Get the url for the checkers view
    url = app.url_for('tree.render_tree')

    # Retrieve the page
    response = await test_client.get(url)
    body = await response.text()

    # The client loads 'tests/document/example7'
    # tests/document/example7/
    # └── src
    #     ├── file1.dm
    #     └── sub1
    #         ├── file11.dm
    #         └── subsub1
    #             └── file111.dm
    assert response.status == 200
    assert 'source' in body
    assert 'file1.dm' in body
    assert 'sub1/file11.dm' in body
    assert 'sub1/subsub1/file111.dm' in body
