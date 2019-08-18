"""
View for checkers.
"""
from .blueprints import system
from ..templates import render_template
from ...checkers import Checker, All, Any, Optional


def checker_to_dict(item, required=True, level=1):
    """Convert checkers into a list of dicts suitable for rendering the view."""
    d = dict()

    d['level'] = level

    # Setup the status string
    available = getattr(item, 'available', None)
    if available is True:
        d['status'] = 'ok'
    elif available is False and required:
        d['status'] = 'fail'
    elif available is False and not required:
        d['status'] = 'missing'
    else:
        d['status'] = 'unknown'

    if isinstance(item, All):
        # All are required
        msg = "Checking required dependencies for '{}'".format(item.category)
        d['msg'] = msg
        d['name'] = item.category
        d['subcheckers'] = [checker_to_dict(i, required=True, level=level + 1)
                      for i in item]

    elif isinstance(item, Any):
        # One is required are required
        msg = "Checking alternative dependencies for '{}'".format(item.category)
        d['msg'] = msg
        d['name'] = item.category
        d['subcheckers'] = [checker_to_dict(i, required=False, level=level + 1)
                      for i in item]

    elif isinstance(item, Optional):
        # Optional
        # One is required are required
        msg = "Checking alternative dependencies for '{}'".format(item.category)
        d['msg'] = msg
        d['name'] = item.category
        d['subcheckers'] = [checker_to_dict(i, required=False, level=level + 1)
                      for i in item]

    elif hasattr(item, 'name'):
        msg = "Checking dependency '{}'".format(item.name)
        d['name'] = item.name
        d['msg'] = msg

    return d


@system.route('/check.html')
async def render_checkers(request):
    """Render the view for software dependency checkers."""
    # Get the checkers
    checker_subclses = Checker.checker_subclasses()
    checkers = [checker_subcls() for checker_subcls in checker_subclses]

    # run the checks
    [checker.check() for checker in checkers]

    # Convert the checkers to a list of dicts
    checkers = map(checker_to_dict, checkers)

    return render_template('checkers.html', request=request,
                           checkers=checkers)
