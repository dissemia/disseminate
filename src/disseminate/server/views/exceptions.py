"""
Views for exceptions.
"""
from flask import render_template, request

from traceback import extract_tb, format_list


def handle_500(exception):
    """Handler for 500 exceptions."""
    traceback = (format_list(extract_tb(exception.__traceback__))
                 if hasattr(exception, '__traceback__') else [])

    template = render_template('server/500.html', request=request,
                             exception=exception, traceback=traceback)
    return template, 500


def handle_404(exception):
    """Handler for 404 exceptions."""
    template = render_template('server/404.html', request=request,
                               exception=exception)
    return template, 404
