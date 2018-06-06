"""
Utilities for tags.
"""
from .. import ast
from .. import settings


def set_html_tag_attributes(html_tag, attrs_dict):
    """Set the attributes for a (html) tag with the values in the given ordered
    dict.

    This function is needed to preserve the order of attributes set for an
    html tag.
    """
    for k, v in attrs_dict.items():
        html_tag.set(k, v)


def format_label_tag(tag, target=None):
    """Produce a string for a reference or label to or from a tag.

    This function only returns a new set of sub-tags for the label. It ignores
    the tag's content and caption, which should be handled by the tag itself.

    The label format is search in the following places, in the following order,
    and returns the first one found.

    1. A 'fmt' attribute in the tag.
    2. The document's context specifying a label's kind.
       ex: figure_label: Fig. {label.number}
    3. Module settings.
    """
    # Get the tag's label
    label = tag.label
    assert label is not None

    # Find the best label string, starting from the most specific kind to the
    # least--then try a default label.
    label_fmt = tag.get_attribute('fmt', target=target, clear=True)

    # See if the fmt was specified in the tag. If not, find one elsewhere.
    if label_fmt is None:
        label_fmt = ""
        for kind in list(reversed(label.kind)) + ['default']:
            # Go through kinds, ex: 'figure' or 'chapter'

            # Construct the name of the label to search for. Ex: figure_label or
            # chapter_label_tex.
            label_name = kind + '_label'
            label_name_target = (label_name + '_' + target.strip('.')
                                 if target is not None else label_name)

            # Try to find the value in the context
            if label_name in tag.context:
                label_fmt = tag.context[label_name]
                break
            if label_name_target in tag.context:
                label_fmt = tag.context[label_name_target]
                break

            # Next check to see if it's the settings. No loop break is done here
            # because a better label might be found in the less specific kinds.
            # To keep the settings clean, these are just referred to by the
            # 'kind'. ex: 'chapter' or 'chapter_html'
            label_name = kind
            label_name_target = (label_name + '_' + target.strip('.')
                                 if target is not None else label_name)

            if label_name in settings.label_fmt:
                label_fmt = settings.label_fmt[label_name]
            if label_name_target in settings.label_fmt:
                label_fmt = settings.label_fmt[label_name_target]

    # A label format string has been found. Now format it.
    label_string = label_fmt.format(label=label)

    # Format any tags
    label_tag = ast.process_ast(label_string, context=tag.context)
    label_tag.name = 'label'  # convert tag name from 'root' to 'label'
    return label_tag


def label_term(tag, target=None):
    """Return the label terminator character(s)."""
    label_term = settings.label_fmt['label_term']

    if 'label_term' in tag.content:
        label_term = tag.content['label_term']

    label_term_attr = tag.get_attribute('label_term', clear=True, target=target)

    if label_term_attr is not None:
        label_term = label_term_attr

    return label_term
