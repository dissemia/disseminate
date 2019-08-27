"""
Views for exceptions.
"""
from traceback import extract_tb, format_list

from ..templates import render_template


async def handle_500(request, exception):
    """Handler for 500 exceptions."""
    traceback = (format_list(extract_tb(exception.__traceback__))
                 if hasattr(exception, '__traceback__') else [])

    return render_template('server/500.html', request=request,
                           exception=exception, traceback=traceback)


async def handle_404(request, exception):
    """Handler for 404 exceptions."""
    return render_template('server/404.html', request=request,
                           exception=exception)
