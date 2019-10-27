"""
Test the signals view.
"""


async def test_view_signals(app, test_client):
    """Test the rendering of the checkers view."""
    # Get the url for the checkers view
    url = app.url_for('system.render_signals')

    # Retrieve the page
    response = await test_client.get(url)
    body = await response.text()

    assert response.status == 200
    assert 'Signals Listing' in body
