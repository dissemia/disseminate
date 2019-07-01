"""
Handlers for error pages
"""
from flask import render_template


def page_not_found(e):
    """Render page for file not found."""
    return render_template('server/404.html'), 404
