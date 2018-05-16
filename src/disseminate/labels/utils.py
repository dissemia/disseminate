"""
Utilities for labels.
"""
from ..ast.utils import flatten_ast


def label_latest_mtime(ast, context):
    """Traverse an Abstract Syntax Tree and report the lastest modification
    time of labels from tags.

    Parameters
    ----------
    ast : tag or list
        The Abstract Syntax Tree
    context : dict
        The context dictionary for the document.

    Returns
    -------
    max_mtime : float or None
        The maximum mtime, if labels were found in the ast or,
        None if no labels were found.
    """
    # Get the label_manager
    if 'label_manager' not in context:
        return None
    label_manager = context['label_manager']

    # Get a flattened_list of tags for the ast
    flattened_ast = flatten_ast(ast, filter_tags=True)

    # Get the label_ids and labels for this tags
    label_ids = {tag.label_id for tag in flattened_ast
                 if hasattr(tag, 'label_id') and tag.label_id is not None}
    labels = [label for label in label_manager.labels if label.id in label_ids]

    # Get the label mtimes
    label_mtimes = [label.mtime for label in labels]

    # Note: each label may have a document_label, chapter_label and so on.
    # The mtimes for these should be checked as well, but since these are
    # internal to a document, they should already be included in the labels
    # listing, so their mtimes do not need to be checked independently.

    return max(label_mtimes) if len(label_mtimes) else None
