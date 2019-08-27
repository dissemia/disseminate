"""
Views for exceptions.
"""
from traceback import extract_tb, format_list

from ..templates import render_template


async def handle_500(request, exception):
    """Handler for 500 exceptions."""
    traceback = (format_list(extract_tb(exception.__traceback__))
                 if hasattr(exception, '__traceback__') else [])

    response = render_template('server/500.html', request=request,
                               exception=exception, traceback=traceback)
    response.status = 500
    return response


async def handle_404(request, exception):
    """Handler for 404 exceptions."""
    response = render_template('server/404.html', request=request,
                                exception=exception)
    response.status = 404
    return response
