"""
Tests the xml formatting functions.
"""
import pytest

from markupsafe import Markup

from disseminate.formats.xhtml import (xml_tag, xml_entity, xhtml_list,
                                       XHtmlFormatError)


def test_xml_tag():
    """Tests the formatting of html_tags."""

    # 1. Test a basic equation with a required argument

    # A required argument is missing; raise an error
    with pytest.raises(XHtmlFormatError):
        xml_tag('img', attributes='')  # 'src' and 'alt' required.

    # 2. Test the formatting of basic tags with required and optional
    # arguments
    #    For the img tag, 'src' is required, 'class' is optional
    assert (xml_tag('img', attributes='src=~/mytest/test.png') ==
            '<img src="~/mytest/test.png"/>\n')

    assert (xml_tag('img',
                      attributes='src=~/mytest/test.png class=myclass')
            == '<img src="~/mytest/test.png" class="myclass"/>\n')

    # 3. Test the formatting of a tag element with non-valid attributes
    assert (xml_tag('img',
                      attributes='src=~/mytest/test.png null=myclass') ==
            '<img src="~/mytest/test.png"/>\n')

    # 4. Test the formatting of a tag with an invalid tag type
    assert (xml_tag('invalid', attributes='null=myclass') ==
            '<span class="invalid"/>\n')

    assert (xml_tag('invalid', attributes='class=myclass') ==
            '<span class="myclass"/>\n')

    # The script tag is not allowed. It will be rendered as a span.
    assert (xml_tag('script', attributes='test') ==
            '<span class="script"/>\n')


def test_xml_entity():
    """Tests the formatting of xml_entity."""

    # 1. Test basic Greek letters
    assert xml_entity('alpha') == '&alpha;\n'
    assert xml_entity('Alpha') == '&Alpha;\n'
    assert xml_entity('beta') == '&beta;\n'

    # 2. Test invalid entities
    assert xml_entity('invalid') == '&invalid;\n'

    # 3. Test html escaping
    with pytest.raises(ValueError):
        assert xml_entity('<script></script>') == ''


def test_xml_escaping():
    """Test the xml_tag function with escaping."""

    # 1. Test basic html escaping
    assert (xml_tag('script', attributes='test',
                    formatted_content='<script>unsafe</script>') ==
            '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n')

    # 2. Test basic html escaping with a list
    assert (xml_tag('script', attributes='test',
                    formatted_content=['<script>unsafe</script>']) ==
            '<span class="script">&lt;script&gt;unsafe&lt;/script&gt;</span>\n')


def test_html_safe_contents():
    """Test the xhtml_tag with safe contents."""

    assert (xml_tag('span', attributes='', formatted_content='<b>test</b>')
            == '<span>&lt;b&gt;test&lt;/b&gt;</span>\n')

    assert (xml_tag('span', attributes='',
                    formatted_content=Markup('<b>test</b>'))
            == ('<span>\n'
                '  <b>test</b>\n'
                '</span>\n'))
