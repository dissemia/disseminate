"""
Function to render the project tree.
"""
from bottle import get, jinja2_view, TEMPLATE_PATH

from .projects import load_projects, template_path
from ..checkers import Checker, All, Any, Optional
from ..document.utils import render_tree_html


TEMPLATE_PATH.append(str(template_path))


## View fpr tree.html

@get('/')
@get('/index.html')
@jinja2_view('tree.html')
def render_tree():
    # Get the documents
    docs = load_projects()
    return {'body': render_tree_html(docs)}


# View for check.html


def checker_to_dict(item, required=True, level=1):
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


@get('/check.html')
@jinja2_view('checkers.html')
def render_checkers():
    # Get the checkers
    checker_subclses = Checker.checker_subclasses()
    checkers = [checker_subcls() for checker_subcls in checker_subclses]

    # run the checks
    [checker.check() for checker in checkers]

    return {'checkers': map(checker_to_dict, checkers)}

