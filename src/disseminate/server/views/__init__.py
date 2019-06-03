from bottle import TEMPLATE_PATH
from ..projects import template_path

# Add the server template path to bottle's template paths
TEMPLATE_PATH.append(str(template_path))

from .tree import render_tree
from .checker import render_checkers
from .processors import render_processors
