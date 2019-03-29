"""
Test the attributes functions
"""
import pytest

from disseminate.attributes import Attributes, PositionalAttribute


def test_attributes_init():
    """Test the creation of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base')
    assert 'class' in attrs
    assert attrs['class'] == 'base'

    attrs = Attributes('class="base btnred" red, style=map',)
    assert attrs.keys() == {'class', 'red', 'style'}
    assert attrs['class'] == 'base btnred'
    assert attrs['red'] == PositionalAttribute
    assert attrs['style'] == 'map'

    # 2. Test with non-conventional arguments
    attrs = Attributes()
    assert len(attrs) == 0

    attrs = Attributes(None)
    assert len(attrs) == 0

    # 3. Test with dicts
    attrs = Attributes({'test': 'class'})
    assert attrs == {'test': 'class'}

    attrs = Attributes(test='class')
    assert attrs == {'test': 'class'}

    attrs = Attributes((('test', 'class'),))
    assert attrs == {'test': 'class'}


def test_attributes_get_by_type():
    """Test the get_by_type method of Attributes classes."""

    # 1. Test the basic conversion of values
    attrs = Attributes('int=1 float=3.2 string=test bool=false tuple="1 2 3"')
    assert attrs.get_by_type('int', int) == 1
    assert attrs.get_by_type('float', float) == 3.2
    assert attrs.get_by_type('string', str) == 'test'
    assert attrs.get_by_type('bool', bool) is False
    assert attrs.get_by_type('tuple', tuple) == ('1', '2', '3')
    assert attrs.get_by_type('tuple', list) == ['1', '2', '3']

    # 2. Try missing entries
    assert 'notint' not in attrs
    assert attrs.get_by_type('notint', int) is None

    with pytest.raises(KeyError):
        attrs.get_by_type('notint', int, raise_error=True)

    # 3. Try type conversions that don't work
    #   3.1 Without raising an error; just return the default
    assert attrs.get_by_type('float', int) is None

    #   3.2 With raising an error.
    with pytest.raises(ValueError):
        attrs.get_by_type('float', int, raise_error=True)

    # 4. Try with target-specific keys
    attrs = Attributes('class=test class.html=htmltest')
    assert attrs.get_by_type('class', target='.html') == 'htmltest'
    assert attrs.get_by_type('class', target='.tex') == 'test'
    assert attrs.get_by_type('class') == 'test'


def test_attributes_append():
    """Test the append method of Attributes classes."""

    # 1. Test the basic conversion of values
    attrs = Attributes()
    attrs.append('test1', '1')
    attrs.append('test1', '2')
    attrs.append('test1', '3')
    assert attrs['test1'] == '1 2 3'

    attrs.append('test2', (1, 2))
    attrs.append('test2', 'test')
    assert attrs['test2'] == '(1, 2) test'


def test_attributes_filter():
    """Test the filter method of Attributes classes."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.filter(target='html') == {'class': 'specific'}
    assert attrs.filter(target='tex') == {'class': 'basic'}

    # 2. Test key filtering
    attrs = Attributes('class=basic width=200 width.tex=300')
    assert attrs.filter(keys='class') == Attributes('class=basic')
    assert attrs.filter(keys='width') == Attributes('width=200')
    assert (attrs.filter(keys='width', target='tex') ==
            Attributes('width=300'))


def test_attributes_exclude():
    """Test the exclude method of Attributes classes."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.exclude('test') == {'class': 'basic', 'class.html': 'specific'}
    assert attrs.exclude('class') == {}
    assert attrs.exclude('test', target='html') == {'class': 'basic',
                                                    'class.html': 'specific'}
    assert attrs.exclude('class', target='tex') == {'class.html': 'specific'}
    assert attrs.exclude(('class', 'test')) == {}


# html targets

def test_attributes_html():
    """Test the formatting of attributes in html."""

    # 1. Test the basic conversion of values
    attrs = Attributes('int=1 float=3.2 string=test bool=false '
                       'tuple="1 2 3" red')
    assert attrs.html == ("int='1' float='3.2' string='test' bool='false' "
                          "tuple='1 2 3' red")

    # 2. Test target-specific attributes
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.html == "class='specific'"

    attrs = Attributes('width.tex=200')
    assert attrs.html == ""


# tex targets

def test_attributes_tex():
    """Test the formatting of attributes in html."""

    # 1. Test the basic conversion of values
    attrs = Attributes('int=1 float=3.2 string=test bool=false '
                       'tuple="1 2 3" red')
    assert attrs.tex == ("int=1 float=3.2 string=test bool=false "
                         "tuple=1 2 3 red")

    # 2. Test target-specific attributes
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.tex == "class=basic"

    attrs = Attributes('width.tex=200')
    assert attrs.tex == "width=200"

    attrs = Attributes('')
    assert attrs.tex == ""
