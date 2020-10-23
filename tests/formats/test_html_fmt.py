"""
Tests for html formatting functions.
"""
import pytest

from markupsafe import Markup

from disseminate.formats import (xhtml_tag, xhtml_entity, xhtml_list,
                                 XHtmlFormatError)


def test_html_tag():
    """Tests the formatting of html_tags."""

    # 1. Test a basic equation with a required argument

    # A required argument is missing; raise an error
    with pytest.raises(XHtmlFormatError):
        xhtml_tag('img', attributes='')

    # 2. Test the formatting of basic tags with required and optional arguments
    #    For the img tag, 'src' is required, 'class' is optional
    assert (xhtml_tag('img', attributes='src=~/mytest/test.png') ==
            '<img src="~/mytest/test.png">\n')

    assert (xhtml_tag('img', attributes='src=~/mytest/test.png class=myclass')
            == '<img src="~/mytest/test.png" class="myclass">\n')

    # 3. Test the formatting of a tag element with non-valid attributes
    assert (xhtml_tag('img', attributes='src=~/mytest/test.png null=myclass') ==
            '<img src="~/mytest/test.png">\n')

    # 4. Test the formatting of a tag with an invalid tag type
    assert (xhtml_tag('invalid', attributes='null=myclass') ==
            '<span class="invalid"></span>\n')

    assert (xhtml_tag('invalid', attributes='class=myclass') ==
            '<span class="myclass"></span>\n')

    assert (xhtml_tag('invalid', attributes='') ==
            '<span class="invalid"></span>\n')

    # The script tag is not allowed. It will be rendered as a span.
    assert (xhtml_tag('script', attributes='test') ==
            '<span class="script"></span>\n')


def test_html_entity():
    """Tests the formatting of xhtml_entity."""

    # 1. Test basic Greek letters
    assert xhtml_entity('alpha') == '&alpha;\n'
    assert xhtml_entity('Alpha') == '&Alpha;\n'
    assert xhtml_entity('beta') == '&beta;\n'

    # 2. Test invalid entities
    assert xhtml_entity('invalid') == '&invalid;\n'

    # 3. Test html escaping
    with pytest.raises(ValueError):
        assert xhtml_entity('<script></script>') == ''


def test_html_escaping():
    """Test the xhtml_tag function with escaping."""

    # 1. Test basic html escaping
    key = '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n'
    assert (xhtml_tag('script', attributes='test',
                      formatted_content='<script>unsafe</script>') ==
            key)

    # 2. Test basic html escaping with a list
    key = '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n'
    assert (xhtml_tag('script', attributes='test',
                      formatted_content=['<script>unsafe</script>']) ==
            key)


def test_html_safe_contents():
    """Test the xhtml_tag with safe contents."""

    assert (xhtml_tag('span', attributes='', formatted_content='<b>test</b>')
            == '<span>&lt;b&gt;test&lt;/b&gt;</span>\n')

    assert (xhtml_tag('span', attributes='',
                      formatted_content=Markup('<b>test</b>'))
            == '<span><b>test</b></span>\n')


def test_html_list():
    """Test the xhtml_list function"""

    # 1. Create a list of list items
    elements = [(0, xhtml_tag('li', formatted_content='1', level=2)),
                (1, xhtml_tag('li', formatted_content='1.1', level=2)),
                (1, xhtml_tag('li', formatted_content='1.2', level=2)),
                (2, xhtml_tag('li', formatted_content='1.2.3', level=2)),
                (0, xhtml_tag('li', formatted_content='2', level=2)),
                (0, xhtml_tag('li', formatted_content='3', level=2)),
                (1, xhtml_tag('li', formatted_content='3.1', level=2))]

    html = xhtml_list(*elements)
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
