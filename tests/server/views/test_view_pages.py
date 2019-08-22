"""
Test the page rendering view.
"""


async def test_view_page(app, test_client):
    """Test the rendering of the checkers view."""
    # Get the url for the checkers view
    project_path = app.config.get('PROJECTPATH')
    url = app.url_for('page.render_page', path='html/file1')

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
    assert '<p>file1.dm</p>' in body
