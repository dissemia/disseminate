"""
Test the attributes functions
"""
import pytest

from disseminate.attributes import Attributes
from disseminate.utils.types import (PositionalValue, FloatPositionalValue,
                                     IntPositionalValue, StringPositionalValue)


def test_attributes_init():
    """Test the creation of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base')
    assert 'class' in attrs
    assert attrs['class'] == 'base'

    attrs = Attributes('class="base btnred" red, style=map',)
    assert attrs.keys() == {'class', 'red', 'style'}
    assert attrs['class'] == 'base btnred'
    assert attrs['red'] == StringPositionalValue
    assert attrs['style'] == 'map'

    # 2a. Test with other characters: '(', ')'
    attrs = Attributes('(a)')
    assert attrs.keys() == {'(a)'}
    assert attrs['(a)'] == StringPositionalValue

    # 2b. Test with other characters: ':', ';', '/', '.'
    attrs = Attributes('sec:file1.dm/test')
    assert attrs.keys() == {'sec:file1.dm/test'}
    assert attrs['sec:file1.dm/test'] == StringPositionalValue

    # 2c. Test with '[' and ']'
    attrs = Attributes('[class="base btnred" red, style=map]', )
    assert attrs.keys() == {'class', 'red', 'style'}
    assert attrs['class'] == 'base btnred'
    assert attrs['red'] == StringPositionalValue
    assert attrs['style'] == 'map'

    # 3. Test with non-conventional arguments
    attrs = Attributes()
    assert len(attrs) == 0

    attrs = Attributes(None)
    assert len(attrs) == 0

    # 4. Test with dicts
    attrs = Attributes({'test': 'class'})
    assert attrs == {'test': 'class'}

    attrs = Attributes(test='class')
    assert attrs == {'test': 'class'}

    attrs = Attributes((('test', 'class'),))
    assert attrs == {'test': 'class'}


def test_attributes_copy():
    """Test the copy method of Attributes classes."""

    assert (Attributes('class="base btnred" red style=map').copy() ==
            Attributes('class="base btnred" red style=map'))


def test_attributes_get_positional():
    """Test the get method of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base 1.tex 2')

    # Positional arguments
    assert attrs.get_positional(PositionalValue, target='tex') == '1'
    assert attrs.get_positional(PositionalValue) == '2'
    assert attrs.get_positional('class') is None

    # 2. Test positional arguments that re-use the attribute separator ('.')
    attrs = Attributes('3.1416 2.718.tex')
    assert attrs.get_positional(PositionalValue, target='tex') == '2.718'
    assert attrs.get_positional(PositionalValue) == '3.1416'
    assert attrs.get_positional(FloatPositionalValue, target='tex') == '2.718'
    assert attrs.get_positional(FloatPositionalValue) == '3.1416'
    assert attrs.get_positional(IntPositionalValue, target='tex') is None
    assert attrs.get_positional(IntPositionalValue) is None


def test_attributes_get():
    """Test the get method of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base 1.tex 2')
    assert attrs.get('class') == 'base'

    # Positional arguments
    assert attrs.get_positional(PositionalValue, target='tex') == '1'
    assert attrs.get_positional(PositionalValue) == '2'
    assert attrs.get(PositionalValue, target='tex') == '1'
    assert attrs.get(PositionalValue) == '2'


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

    # 2. Test with positional arguments
    attrs.append('1')
    attrs.append('2.tex')
    assert attrs['1'] == PositionalValue
    assert attrs['2.tex'] == PositionalValue


def test_attributes_filter():
    """Test the filter method of Attributes classes."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.filter(target='html') == {'class': 'specific'}
    assert attrs.filter(target='tex') == {'class': 'basic'}

    # 2. Test key filtering
    attrs = Attributes('class=basic width=200 width.tex=300')
    assert attrs.filter(attrs='class') == Attributes('class=basic')
    assert attrs.filter(attrs='width') == Attributes('width=200')
    assert (attrs.filter(attrs='width', target='tex') ==
            Attributes('width=300'))

    # 3. Test positional arguments
    attrs = Attributes('class=basic class.html=specific 3.1416 2.718.tex')
    print(attrs.filter(target='tex'))
    assert attrs.filter(target='tex') == Attributes('class=basic '
                                                    '3.1416 2.718')
    assert attrs.filter(target='html') == Attributes('class=specific '
                                                    '3.1416')

    # 4. Test an example for allowed attributes with equations
    attrs = Attributes('class=basic src=img.txt env=alignat* 3')
    filtered_attrs = attrs.filter(attrs=(IntPositionalValue, 'env'),
                                  target='tex')
    assert filtered_attrs == Attributes('env=alignat* 3')

    filtered_attrs = attrs.filter(attrs=(IntPositionalValue,),
                                  target='tex')
    assert filtered_attrs == Attributes('3')


def test_attributes_filter_order():
    """Test the ordering of attributes for the filter method."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('one=1 two=2')

    assert attrs.html == "one='1' two='2'"
    assert attrs.filter(('one', 'two')).html == "one='1' two='2'"
    assert attrs.filter(('two', 'one')).html == "one='1' two='2'"


def test_attributes_exclude():
    """Test the exclude method of Attributes classes."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('class=basic class.html=specific')
    assert attrs.exclude('test') == {'class': 'basic', 'class.html': 'specific'}
    assert attrs.exclude('class') == {}
    assert attrs.exclude('test', target='html') == {'class': 'basic'}
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

    # 3. Test with filter
    attrs = Attributes('src="test" width.html=100 height.tex=20')
    attrs.filter(attrs=('src', 'width', 'height'), target='html')
    assert attrs.html == "src='test' width='100'"


# tex targets

def test_attributes_tex():
    """Test the formatting of attributes in html."""

    # 1. Test arguments
    attrs = Attributes('class=basic src=img.txt env=alignat* 3')
    filtered_attrs = attrs.filter(attrs=(IntPositionalValue,),
                                  target='tex')
    assert filtered_attrs.tex_arguments == '{3}'

    attrs = Attributes('class=basic src=img.txt env=alignat* 3')
    filtered_attrs = attrs.filter(attrs=[], target='tex')
    assert filtered_attrs.tex_arguments == ''

    # 2. Test optionals
    attrs = Attributes('width=1cm')
    filtered_attrs = attrs.filter(attrs=('width', 'height'), target='tex')
    assert filtered_attrs.tex_optionals == '[width=1cm]'

    # 3. Test ordering
    attrs = Attributes('env=alignat* 3')
    assert attrs.tex_arguments == '{alignat*}{3}'

    attrs = Attributes('3 env=alignat*')
    assert attrs.tex_arguments == '{3}{alignat*}'

    # 4. Test ordering with the filter method. By default, items are sorted
    #    by the instantiation order of the original attrs dict
    attrs = Attributes('env=alignat* 3')
    attrs_filtered = attrs.filter(attrs=('env', IntPositionalValue))
    assert attrs_filtered.tex_arguments == '{alignat*}{3}'

    attrs_filtered = attrs.filter(attrs=(IntPositionalValue, 'env'))
    assert attrs_filtered.tex_arguments == '{alignat*}{3}'

    # 5. Test ordering with the filter method, using the sort_by_attrs
    attrs_filtered = attrs.filter(attrs=('env', IntPositionalValue),
                                  sort_by_attrs=True)
    assert attrs_filtered.tex_arguments == '{alignat*}{3}'

    attrs_filtered = attrs.filter(attrs=(IntPositionalValue, 'env'),
                                  sort_by_attrs=True)
    assert attrs_filtered.tex_arguments == '{3}{alignat*}'

