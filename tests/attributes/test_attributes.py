"""
Test the attributes functions
"""
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

    # 5. Test positionals with quoted spaces
    attrs = Attributes('one "{my second positional}"')
    assert attrs['one'] == StringPositionalValue
    assert attrs['{my second positional}'] == StringPositionalValue

    # 6. Test positionals without quoted spaces
    attrs = Attributes('one {my second positional}')
    assert attrs['one'] == StringPositionalValue
    assert attrs['{my'] == StringPositionalValue
    assert attrs['second'] == StringPositionalValue
    assert attrs['positional}'] == StringPositionalValue


def test_attributes_copy():
    """Test the copy method of Attributes classes."""

    assert (Attributes('class="base btnred" red style=map').copy() ==
            Attributes('class="base btnred" red style=map'))


def test_attributes_find_item():
    """Test the find_item method of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base 1.tex 2')
    assert (attrs.find_item(IntPositionalValue, target='tex') ==
            ('1.tex', IntPositionalValue))
    assert (attrs.find_item(PositionalValue, target='tex') ==
            ('1.tex', IntPositionalValue))
    assert attrs.find_item(PositionalValue) == ('2', IntPositionalValue)
    assert attrs.find_item(StringPositionalValue) is None

    # 2. Test positional arguments that re-use the attribute separator ('.')
    attrs = Attributes('3.1416 2.718.tex')
    assert (attrs.find_item(PositionalValue, target='tex') ==
            ('2.718.tex', FloatPositionalValue))
    assert attrs.find_item(PositionalValue) == ('3.1416', FloatPositionalValue)
    assert (attrs.find_item(FloatPositionalValue, target='tex') ==
            ('2.718.tex', FloatPositionalValue))
    assert (attrs.find_item(FloatPositionalValue) ==
            ('3.1416', FloatPositionalValue))
    assert attrs.find_item(IntPositionalValue, target='tex') is None
    assert attrs.find_item(IntPositionalValue) is None

    # 3. Test positional arguments with paths/urls
    attrs = Attributes('link#anchor')
    assert (attrs.find_item(PositionalValue) ==
            ('link#anchor', StringPositionalValue))

    attrs = Attributes('my_file.pdf#link-anchor')
    assert (attrs.find_item(PositionalValue) ==
            ('my_file.pdf#link-anchor', StringPositionalValue))
    assert (attrs.find_item(PositionalValue, target='.tex') ==
            ('my_file.pdf#link-anchor', StringPositionalValue))
    assert (attrs.find_item(StringPositionalValue, target='.tex') ==
            ('my_file.pdf#link-anchor', StringPositionalValue))

    # 3. Test key/value entries
    attrs = Attributes('class="general" class.html="specific"')
    assert attrs.find_item('class') == ('class', 'general')
    assert (attrs.find_item('class', target='.html') ==
            ('class.html', 'specific'))
    assert (attrs.find_item('class', target='.tex') ==
            ('class', 'general'))

    # 4. Test a mix of positional and key/value entries
    attrs = Attributes('class=base 1.tex 2 "my first" "my.second"')
    assert attrs.find_item('class') == ('class', 'base')
    assert attrs.find_item('1', target='.tex') == ('1.tex', IntPositionalValue)
    assert attrs.find_item('1.tex') == ('1.tex', IntPositionalValue)
    assert attrs.find_item('1.html') is None
    assert attrs.find_item('2') == ('2', IntPositionalValue)
    assert attrs.find_item('2', target='tex') == ('2', IntPositionalValue)
    assert attrs.find_item('my first') == ('my first', StringPositionalValue)
    assert (attrs.find_item('my first', target='.html') ==
            ('my first', StringPositionalValue))
    assert attrs.find_item('my.second') == ('my.second', StringPositionalValue)
    assert (attrs.find_item('my.second', target='.html') ==
            ('my.second', StringPositionalValue))


def test_attributes_get():
    """Test the get method of Attributes classes."""

    # 1. Test the parsing for basic strings.
    attrs = Attributes('class=base 1.tex 2 "my first" "my.second"')
    assert attrs.get('class') == 'base'

    # Positional arguments
    assert attrs.get(PositionalValue, target='tex') == '1'
    assert attrs.get(PositionalValue) == '2'

    assert attrs.get('1.tex') == IntPositionalValue
    assert attrs.get('1', target='tex') == IntPositionalValue
    assert attrs.get('1', target='html') is None

    assert attrs.get('2') == IntPositionalValue
    assert attrs.get('2', target='tex') == IntPositionalValue

    assert attrs.get('my first') == StringPositionalValue
    assert attrs.get('my first', target='tex') == StringPositionalValue

    assert attrs.get('my.second') == StringPositionalValue
    assert attrs.get('my.second', target='tex') == StringPositionalValue


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


def test_attributes_strip():
    """Test the strip method of Attributes classes."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('class=basic class.html=specific two')
    assert len(attrs) == 3

    attrs.strip()
    assert len(attrs) == 2
    assert attrs['class'] == 'specific'
    assert attrs['two'] == StringPositionalValue


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
    assert attrs.filter(target='tex') == Attributes('class=basic '
                                                    '3.1416 2.718')
    assert attrs.filter(target='html') == Attributes('class=specific '
                                                     '3.1416')

    # 4. Test examples for allowed attributes with equations
    attrs = Attributes('class=basic src=img.txt env=alignat* 3')
    filtered_attrs = attrs.filter(attrs=(IntPositionalValue, 'env'),
                                  target='tex')
    assert filtered_attrs == Attributes('env=alignat* 3')

    filtered_attrs = attrs.filter(attrs=(IntPositionalValue,),
                                  target='tex')
    assert filtered_attrs == Attributes('3')

    # 5. Test examples with paths
    attrs = Attributes('my_file.pdf#link-anchor')
    filtered_attrs = attrs.filter(attrs=(StringPositionalValue,),
                                  target='tex')
    assert 'my_file.pdf#link-anchor' in filtered_attrs

    filtered_attrs = attrs.filter(attrs=(StringPositionalValue,),
                                  target='tex',
                                  sort_by_attrs=True)
    assert 'my_file.pdf#link-anchor' in filtered_attrs

    # Filtering without a target attribute works
    filtered_attrs = attrs.filter(target='tex')
    assert 'my_file.pdf#link-anchor' in filtered_attrs

    # 6. Test examples with quoted spaces
    # 6.1. Test an example with quoted spaces in the value
    attrs = Attributes('class="image one"')
    filtered_attrs = attrs.filter(attrs='class')
    assert filtered_attrs['class'] == "image one"

    # 6.1. Test an example with quoted spaces in the positional value
    attrs = Attributes('one "two three"')
    assert 'one' in attrs
    assert 'two three' in attrs

    filtered_attrs = attrs.filter(attrs=('one', 'two three'))
    assert 'one' in filtered_attrs
    assert 'two three' in filtered_attrs

    filtered_attrs = attrs.filter(attrs=('one', 'two three'), target='.html')
    assert 'one' in filtered_attrs
    assert 'two three' in filtered_attrs

    # 6.2. Test an example with quoted spaces and periods in the positional
    # value
    attrs = Attributes('one "{http://link.org/}type"')
    assert 'one' in attrs
    assert '{http://link.org/}type' in attrs

    filtered_attrs = attrs.filter(attrs=('one', '{http://link.org/}type'))
    assert 'one' in filtered_attrs
    assert '{http://link.org/}type' in filtered_attrs

    filtered_attrs = attrs.filter(attrs=('one', '{http://link.org/}type'),
                                  target='.xhtml')
    assert 'one' in filtered_attrs
    assert '{http://link.org/}type' in filtered_attrs


def test_attributes_filter_order():
    """Test the ordering of attributes for the filter method."""

    # 1. Test target-specific and non-target-specific targets
    attrs = Attributes('one=1 two=2')

    assert attrs.html == "one='1' two='2'"
    assert attrs.filter(('one', 'two')).html == "one='1' two='2'"
    assert attrs.filter(('two', 'one')).html == "one='1' two='2'"


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
    assert attrs.html == "class='basic' class.html='specific'"
    attrs = attrs.filter(target='.html')
    assert attrs.html == "class='specific'"

    attrs = Attributes('width.tex=200').filter(target='html')
    assert attrs.html == ""

    # 3. Test with filter
    attrs = Attributes('src="test" width.html=100 height.tex=20')
    attrs = attrs.filter(attrs=('src', 'width', 'height'), target='html')
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

    # 5. Test paths and urls. Without specifying the '.tex' target, an
    #    argument is not returned
    attrs = Attributes('my_file.pdf#link-anchor')
    assert attrs.tex_arguments == "{my_file.pdf#link-anchor}"

    # But it does work with a target attribute
    attrs = Attributes('my_file.pdf#link-anchor.tex').filter(target='.tex')
    assert attrs.tex_arguments == "{my_file.pdf#link-anchor}"
