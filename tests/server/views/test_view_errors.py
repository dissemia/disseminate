"""
Test handler views for errors
"""


async def test_view_404(app, test_client):
    """Test the rendering of 404 page."""

    # Retrieve the page
    response = await test_client.get('/html/page-does-not-exist.html')
    body = await response.text()

    assert response.status == 404
    assert "File not Found" in body
