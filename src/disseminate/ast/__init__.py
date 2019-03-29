"""
Abstract syntax trees (ASTs) are trees of tags formed by tags that have lists
of strings and tags as their content. The AST processing functions convert
strings into ASTs (tag trees) and process the ASTs.
"""

from .ast import AstException, process_ast, process_context_asts
from .paragraph import process_paragraphs, process_context_paragraphs
from .typography import process_typography, process_context_typography
from . import utils, exceptions
