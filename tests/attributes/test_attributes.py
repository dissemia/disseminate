"""
Test the attributes functions
"""
import pytest

from disseminate.attributes import (TagAttributeError, parse_attributes,
                                    get_attribute_value, set_attribute,
                                    filter_attributes, kwargs_attributes,
                                    format_html_attributes,
                                    format_tex_attributes)


def test_parse_attributes():
    """Test the parse_attributes function."""

    # Test the order of attributes
    assert (parse_attributes(" class='base bttnred' style= media red") ==
            (('class', 'base bttnred'), ('style', 'media'), 'red'))
    assert (parse_attributes("style= media class='base bttnred' red") ==
            (('style', 'media'), ('class', 'base bttnred'), 'red'))


def test_get_attribute_value():
    """Test the get_attribute_value function."""

    attrs1 = (('class', 'base bttnred'), ('style', 'media'), 'red')
    assert get_attribute_value(attrs1, 'style') == 'media'
    assert get_attribute_value(attrs1, 'red') == 'red'
    assert get_attribute_value(attrs1, 'missing') is None


def test_set_attribute():
    """Test the set_attribute function."""

    attrs1 = (('class', 'base bttnred'), ('style', 'media'), 'red')
    assert (set_attribute(attrs1, ('class', 'standard'), method='r') ==
            (('class', 'standard'), ('style', 'media'), 'red'))
    assert (set_attribute(attrs1,  ('class', 'standard'), method='a') ==
            (('class', 'base bttnred'), ('style', 'media'), 'red',
             ('class', 'standard')))
    assert (set_attribute(attrs1, 'red', method='r') ==
            (('class', 'base bttnred'), ('style', 'media'), 'red'))
    assert (set_attribute(attrs1, 'red', method='a') ==
            (('class', 'base bttnred'), ('style', 'media'), 'red', 'red'))


def test_filter_attributes():
    """Test the filter_attributes function."""

    attrs1 = (('class', 'base'), ('style', 'media'), 'red')

    # Setting attribute_names and target to None doesn't filter items
    assert (filter_attributes(attrs=attrs1) == attrs1)
    assert (filter_attributes(attrs=attrs1, attribute_names=None,
                              target=None) == attrs1)

    # Setting the target doesn't filter non-specific target items
    assert (filter_attributes(attrs=attrs1, target='.tex') == attrs1)

    # Setting the attributes to include a specific target item includes that
    # item
    attrs2 = (('tex.class', 'base'), ('style', 'media'), 'red')
    assert (filter_attributes(attrs=attrs2, target='.tex') ==
            (('class', 'base'), ('style', 'media'), 'red'))
    assert (filter_attributes(attrs=attrs2, target='.html') ==
            (('style', 'media'), 'red'))
    assert (filter_attributes(attrs=attrs2) ==
            (('style', 'media'), 'red'))

    # Select my attribute names
    assert (filter_attributes(attrs=attrs2, target='.tex') ==
            (('class', 'base'), ('style', 'media'), 'red'))
    assert (filter_attributes(attrs=attrs2, attribute_names=['class'],
                              target='.tex') ==
            (('class', 'base'),))
    assert (filter_attributes(attrs=attrs2, attribute_names=['style'],
                              target='.tex') ==
            (('style', 'media'),))
    assert (filter_attributes(attrs=attrs2, attribute_names=['red'],
                              target='.tex') ==
            ('red',))
    assert (filter_attributes(attrs=attrs2, attribute_names=[],
                              target='.tex') ==
            ())

    # Test exceptions
    filter_attributes(attrs=attrs2, attribute_names=['missing'],
                      target='.tex', raise_error=False)
    with pytest.raises(TagAttributeError):
        filter_attributes(attrs=attrs2, attribute_names=['missing'],
                          target='.tex', raise_error=True)


def test_kwargs_attributes():
    """Test the kwargs_attributes function."""

    # Test a basic conversion
    attrs1 = (('class', 'base'), ('style', 'media'), 'red')
    assert (kwargs_attributes(attrs1) ==
            {'class': 'base', 'style': 'media'})
    assert (kwargs_attributes(attrs1, attribute_names=['class']) ==
            {'class': 'base'})
    assert (kwargs_attributes(attrs1, target='.tex') ==
            {'class': 'base', 'style': 'media'})

    # Test conversion with target-specific attributes
    attrs2 = (('tex.class', 'base'), ('style', 'media'), 'red')
    assert (kwargs_attributes(attrs2) ==
            {'style': 'media'})
    assert (kwargs_attributes(attrs2, attribute_names=['class']) ==
            {})
    assert (kwargs_attributes(attrs2, target='.tex') ==
            {'class': 'base', 'style': 'media'})

    # Test exceptions
    kwargs_attributes(attrs=attrs2, attribute_names=['missing'],
                      target='.tex', raise_error=False)
    with pytest.raises(TagAttributeError):
        kwargs_attributes(attrs=attrs2, attribute_names=['missing'],
                          target='.tex', raise_error=True)


def test_format_html_attributes():
    """Test the format_html_attributes function."""

    # Test a basic conversion
    attrs1 = (('class', 'base'), ('style', 'media'), 'red')
    assert (format_html_attributes(attrs1) ==
            "class='base' style='media' red")

    # Test filtering of attribute_names and specific targets
    assert (format_html_attributes(attrs1, attribute_names=['style']) ==
            "style='media'")

    attrs2 = (('tex.class', 'base'), ('style', 'media'))
    assert (format_html_attributes(attrs2) == "style='media'")

    attrs3 = (('html.class', 'base'), ('style', 'media'))
    assert (format_html_attributes(attrs3) == "class='base' style='media'")


def test_format_tex_attributes():
    """Test the format_tex_attributes function."""
    # Test a basic conversion
    attrs1 = (('class', 'base'), ('style', 'media'), 'red')
    assert (format_tex_attributes(attrs1) ==
            "[class=base, style=media, red]")

    # Test filtering of attribute_names and specific targets
    assert (format_tex_attributes(attrs1, attribute_names=['style']) ==
            "[style=media]")

    attrs2 = (('tex.class', 'base'), ('style', 'media'))
    assert (format_tex_attributes(attrs2) == "[class=base, style=media]")

    attrs3 = (('html.class', 'base'), ('style', 'media'))
    assert (format_tex_attributes(attrs3) == "[style=media]")
