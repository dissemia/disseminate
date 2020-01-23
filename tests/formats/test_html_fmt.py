"""
Tests for tex formatting functions for tags.
"""
import pytest

from markupsafe import Markup

from disseminate.formats import (html_tag, html_entity, html_list,
                                 HtmlFormatError)


def test_html_tag():
    """Tests the formatting of html_tags."""

    # 1. Test a basic equation with a required argument

    # A required argument is missing; raise an error
    with pytest.raises(HtmlFormatError):
        html_tag('img', attributes='')

    # 2. Test the formatting of basic tags with required and optional arguments
    #    For the img tag, 'src' is required, 'class' is optional
    key = '<img src="~/mytest/test.png">\n'
    assert (html_tag('img', attributes='src=~/mytest/test.png') ==
            key)

    key = '<img src="~/mytest/test.png" class="myclass">\n'
    assert (html_tag('img', attributes='src=~/mytest/test.png class=myclass') ==
            key)

    # 3. Test the formatting of a tag element with non-valid attributes
    key = '<img src="~/mytest/test.png">\n'
    assert (html_tag('img', attributes='src=~/mytest/test.png null=myclass') ==
            key)

    # 4. Test the formatting of a tag with an invalid tag type
    key = '<span class="invalid"></span>\n'
    assert (html_tag('invalid', attributes='null=myclass') ==
            key)

    key = '<span class="invalid"></span>\n'
    assert (html_tag('invalid', attributes='class=myclass') ==
            key)

    # The script tag is not allowed. It will be rendered as a span.
    key = '<span class="script"></span>\n'
    assert (html_tag('script', attributes='test') ==
            key)


def test_html_entity():
    """Tests the formatting of html_entity."""

    # 1. Test basic Greek letters
    assert html_entity('alpha') == '&alpha;\n'
    assert html_entity('Alpha') == '&Alpha;\n'
    assert html_entity('beta') == '&beta;\n'

    # 2. Test invalid entities
    assert html_entity('invalid') == '&invalid;\n'

    # 3. Test html escaping
    with pytest.raises(ValueError):
        assert html_entity('<script></script>') == ''


def test_html_escaping():
    """Test the html_tag function with escaping."""

    # 1. Test basic html escaping
    key = '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n'
    assert (html_tag('script', attributes='test',
                     formatted_content='<script>unsafe</script>') ==
            key)

    # 2. Test basic html escaping with a list
    key = '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n'
    assert (html_tag('script', attributes='test',
                     formatted_content=['<script>unsafe</script>']) ==
            key)


def test_html_safe_contents():
    """Test the html_tag with safe contents."""

    assert (html_tag('span', attributes='', formatted_content='<b>test</b>')
            == '<span>&lt;b&gt;test&lt;/b&gt;</span>\n')

    assert (html_tag('span', attributes='',
                     formatted_content=Markup('<b>test</b>'))
            == '<span><b>test</b></span>\n')


def test_html_list():
    """Test the html_list function"""

    # 1. Create a list of list items
    elements = [(0, html_tag('li', formatted_content='1', level=2)),
                (1, html_tag('li', formatted_content='1.1', level=2)),
                (1, html_tag('li', formatted_content='1.2', level=2)),
                (2, html_tag('li', formatted_content='1.2.3', level=2)),
                (0, html_tag('li', formatted_content='2', level=2)),
                (0, html_tag('li', formatted_content='3', level=2)),
                (1, html_tag('li', formatted_content='3.1', level=2))]

    html = html_list(*elements)
    assert html == ('<ol>\n'
                      '<li>1</li>\n'
                      '<ol>\n'
                        '<li>1.1</li>\n'
                        '<li>1.2</li>\n'
                        '<ol>'
                          '<li>1.2.3</li>'
                        '</ol>\n'
                      '</ol>\n'
                      '<li>2</li>\n'
                      '<li>3</li>\n'
                      '<ol>'
                        '<li>3.1</li>'
                      '</ol>\n'
                    '</ol>\n')
