"""
Utilities for tags.
"""


def set_html_tag_attributes(html_tag, attrs_dict):
    """Set the attributes for an html tag with the values in the given ordered
    dict.

    This function is needed to preserve the order of attributes set for an
    html tag. It is designed to be used with the lxml tag API.
    """
    for k, v in attrs_dict.items():
        html_tag.set(k, v)
