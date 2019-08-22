"""
Test the processors view.
"""


async def test_view_processors(app, test_client):
    """Test the rendering of the checkers view."""
    # Get the url for the checkers view
    url = app.url_for('system.render_processors')

    # Retrieve the page
    response = await test_client.get(url)
    body = await response.text()

    assert response.status == 200
    assert 'ProcessTag' in body
