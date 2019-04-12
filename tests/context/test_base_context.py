"""
Tests for the BaseContext class.
"""
import pytest
import copy

from disseminate.context import BaseContext


def test_base_context_dict():
    """Test the basic dict functionality of the base context class."""

    # initialize from kwargs
    context = dict(a=1, b=2, c=3)
    assert context['a'] == 1
    assert context['b'] == 2
    assert context['c'] == 3

    # initialize from tuples
    context = BaseContext((('a', 1), ('b', 2), ('c', 3)))
    assert context['a'] == 1
    assert context['b'] == 2
    assert context['c'] == 3

    # Test standard dict retrieval methods
    assert context['a'] == 1
    assert context.get('a', None) == 1
    assert context.get('not a', None) is None

    with pytest.raises(KeyError):
        not_a = context['not a']

    # Test the set methods
    assert context.setdefault('d', 4) == 4
    assert 'd' in context
    assert context['d'] == 4

    context['g'] = context.get('g', 2)
    assert context['g'] == 2


def test_base_context_inheritance(context_cls):
    """Test the BaseContext inheritance with the parent dict."""

    grand_parent = dict(a=2, b=3, c=4)
    parent = context_cls(d=5, e=6, f=7, parent_context=grand_parent)
    child = context_cls(g=8, parent_context=parent)

    # 1. Test basic accessors for the grand_parent
    assert grand_parent['a'] == 2
    assert grand_parent.get('a') == 2
    assert grand_parent['b'] == 3
    assert grand_parent.get('b') == 3
    assert grand_parent['c'] == 4
    assert grand_parent.get('c') == 4
    assert grand_parent.get('d') is None

    # test keys and len
    assert grand_parent.keys() == {'a', 'b', 'c'}
    assert set(grand_parent.values()) == {2, 3, 4}
    assert grand_parent.items() == {('a', 2), ('b', 3), ('c', 4)}

    assert all(k in grand_parent for k in {'a', 'b', 'c'})

    assert len(grand_parent) == 3

    # 2. Test basic accessors for the parent
    assert parent['a'] == 2
    assert parent.get('a') == 2
    assert parent['b'] == 3
    assert parent.get('b') == 3
    assert parent['c'] == 4
    assert parent.get('c') == 4
    assert parent['d'] == 5
    assert parent.get('d') == 5
    assert parent['e'] == 6
    assert parent.get('e') == 6
    assert parent['f'] == 7
    assert parent.get('f') == 7
    assert parent.get('g') is None

    # test keys and len
    assert parent.keys(only_self=True) == {'d', 'e', 'f'}
    assert parent.keys() == {'a', 'b', 'c', 'd', 'e', 'f'}
    assert set(parent.values(only_self=True)) == {5, 6, 7}
    assert set(parent.values()) == {2, 3, 4, 5, 6, 7}
    assert set(parent.items(only_self=True)) == {('d', 5), ('e', 6), ('f', 7)}
    assert set(parent.items()) == {('a', 2), ('b', 3), ('c', 4),
                                   ('d', 5), ('e', 6), ('f', 7)}

    assert all(k in parent for k in {'a', 'b', 'c', 'd', 'e', 'f'})

    assert len(parent) == 6
    assert parent.len(only_self=True) == 3
    assert parent.len() == 6

    # iter should return all elements
    assert dict(**parent).items() == {('a', 2), ('b', 3), ('c', 4),
                                      ('d', 5), ('e', 6), ('f', 7)}

    # 2. Test basic accessors for the child
    assert child['a'] == 2
    assert child.get('a') == 2
    assert child['b'] == 3
    assert child.get('b') == 3
    assert child['c'] == 4
    assert child.get('c') == 4
    assert child['d'] == 5
    assert child.get('d') == 5
    assert child['e'] == 6
    assert child.get('e') == 6
    assert child['f'] == 7
    assert child.get('f') == 7
    assert child['g'] == 8
    assert child.get('g') == 8

    # test keys and len
    assert child.keys(only_self=True) == {'g'}
    assert child.keys() == {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
    assert set(child.values(only_self=True)) == {8}
    assert set(child.values()) == {2, 3, 4, 5, 6, 7, 8}
    assert set(child.items(only_self=True)) == {('g', 8)}
    assert set(child.items()) == {('a', 2), ('b', 3), ('c', 4),
                                  ('d', 5), ('e', 6), ('f', 7),
                                  ('g', 8)}

    assert all(k in child for k in {'a', 'b', 'c', 'd', 'e', 'f', 'g'})

    assert len(child) == 7
    assert child.len(only_self=True) == 1
    assert child.len() == 7

    # iter should return all elements
    assert dict(**child).items() == {('a', 2), ('b', 3), ('c', 4),
                                     ('d', 5), ('e', 6), ('f', 7),
                                     ('g', 8)}


def test_base_context_do_not_inherit(context_cls):
    """Test the behavior of the 'do_not_inherit' attribute with parent classes
    and sub-classes."""

    class SubContext(context_cls):

        do_not_inherit = {'a'}

    sub_parent = SubContext(a=1, b=2)
    sub_child = SubContext(parent_context=sub_parent)

    # Test access to the keys. The sub_child should have access to 'b' but not
    # 'a'
    assert 'a' not in sub_child
    assert 'a' not in sub_child.keys(only_self=True)
    assert 'a' not in sub_child.keys()

    assert 'b' in sub_child
    assert 'b' not in sub_child.keys(only_self=True)
    assert 'b' in sub_child.keys()

    with pytest.raises(KeyError):
        sub_child['a']
    assert sub_child['b'] == 2

    # Now populate 'a' and 'b' for the sub_child, and these should be accessible
    # as normal
    sub_child['a'] = 3
    sub_child['b'] = 4

    assert 'a' in sub_child
    assert 'a' in sub_child.keys(only_self=True)
    assert 'a' in sub_child.keys()

    assert 'b' in sub_child
    assert 'b' in sub_child.keys(only_self=True)
    assert 'b' in sub_child.keys()

    assert sub_child['a'] == 3
    assert sub_child['b'] == 4

    # Make sure the parent's values haven't changed
    assert sub_parent['a'] == 1
    assert sub_parent['b'] == 2


def test_base_context_load(context_cls):
    """The the load method of the base context."""

    test = """
    ---
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    ---
    body
    """
    context = context_cls()
    context.load(test)

    assert 'contact' in context
    assert context['contact'] == '  address: 1,2,3 lane\n  phone: 333-333-4123.'

    assert 'name' in context
    assert context['name'] == 'Justin L Lorieau'

    assert 'address' not in context
    assert 'phone' not in context

    # Make sure the header portion was the only part loaded
    assert not any('body' in k or 'body' in v for k, v in context.items())


def test_base_context_reset(context_cls):
    """Test the reset functionality in the base context."""

    # Setup the context and parent_context
    parent_context = context_cls(**{'a': 2, 'b': 3, 'c': 4, 'd': 5, 'e': 6,
                                    'h': []})
    context = context_cls(parent_context=parent_context, f=7, g=8)
    context['i'] = 9

    assert context['a'] == 2
    assert context['b'] == 3
    assert context['c'] == 4
    assert context['d'] == 5
    assert context['e'] == 6
    assert context['f'] == 7
    assert context['g'] == 8
    assert context['h'] == []
    assert context['i'] == 9

    # Try changing values in the context
    context['a'] = -2
    context['d'] = 5

    # Reset should remove entries but keep the default context, parent_context
    # and initial_value entries
    context.reset()
    assert context['a'] == 2
    assert context['b'] == 3
    assert context['c'] == 4
    assert context['d'] == 5
    assert context['e'] == 6
    assert context['f'] == 7
    assert context['g'] == 8
    assert context['h'] == []
    assert 'i' not in context


def test_base_context_is_valid(context_cls):
    """Tests the 'is_valid' method in the BaseContext."""

    # We use the context_cls fixture, which is a BaseContext class instance,
    # because we are modifying the BaseContext class

    default_validation_types = context_cls.validation_types
    context_cls.validation_types = {'int': int,
                                    'float': float,
                                    'str': str,
                                    'set': set,
                                    }

    # 1. test a context with missing entries
    context = context_cls(b=2, c=3)
    assert not context.is_valid()

    # 2. test a context with the wrong types
    context = context_cls(int=3.2, float=4, str=None)
    assert not context.is_valid()

    # 3. test a context with the right types, but one missing.
    context = context_cls(int=4, float=3.2, set={1,2,3})
    assert not context.is_valid()
    assert context.is_valid(must_exist=False)

    context_cls.validation_types = default_validation_types

    # 4. Alternatively, we could only check specific keys
    assert context.is_valid('int', 'float', 'set')

    # 5. and missing keys
    with pytest.raises(AssertionError):
        assert context.is_valid('missing')


def test_base_context_mutables(context_cls):
    """Test changes to mutables from parents and children context class
    objects."""

    # Setup a parent and child contexts with a mutables
    parent = context_cls(paths=[])
    child = context_cls(parent_context=parent)

    parent['paths'].append(1)
    child['paths'].append(2)

    assert parent['paths'] == [1, 2]
    assert child['paths'] == [1, 2]

    # Now replace the paths in the child
    child['paths'] = []

    parent['paths'].append(3)
    child['paths'].append(4)

    assert parent['paths'] == [1, 2, 3]
    assert child['paths'] == [4]


def test_base_context_match_update(a_in_b):
    """Tests the recursive update method for the BaseContext."""

    # Converts a string to a dict
    context = BaseContext()
    context.matched_update('test: one')
    assert a_in_b({'test': 'one'}, context)

    # Existing values are overwritten
    context = BaseContext(test='one')
    context.matched_update('test: two')
    assert a_in_b({'test': 'two'}, context)

    # Types are not changed
    context = BaseContext(test=1)
    context.matched_update('test: two')
    assert a_in_b({'test': 1}, context)

    # Unless they can be converted
    context = BaseContext(test=1)
    context.matched_update('test: 2')
    assert a_in_b({'test': 2}, context)

    # Try a dict entry with a mismatched type
    context = BaseContext(test={'a': 1})
    context.matched_update('test: 2')
    assert a_in_b({'test': {'a': 1}}, context)

    # Try a dict entry with a dict change
    context = BaseContext(test={'a': 1})
    context.matched_update('test:\n  a: 2')
    assert a_in_b({'test': {'a': 2}}, context)

    context = BaseContext(test={'a': 1})
    context.matched_update('test:\n  b: 2')
    assert a_in_b({'test': {'a': 1, 'b': '2'}}, context)

    # Try bool entries
    context = BaseContext(test=True)
    context.matched_update('test: false')
    assert a_in_b({'test': False}, context)

    context = BaseContext(test=1)
    context.matched_update('test: false')
    assert a_in_b({'test': 1}, context)

    # Try a list entry
    context = BaseContext(paths=['one', 'two'])
    context.matched_update('paths: three')
    assert a_in_b({'paths': ['three', 'one', 'two']}, context)

    # The initial value mutables have not changed
    assert context['_initial_values'] == {'paths': ['one', 'two']}

    # Hidden entries are not touched
    context = BaseContext(a=1)
    context.matched_update('_initial_values:\n  b: 2')
    assert context['_initial_values'] == {'a': 1}


def test_base_context_match_update_with_inheritance(context_cls):
    """Tests the recursive update method for the BaseContext with
    inheritance."""

    # Setup the contexts
    parent_context = context_cls(a_list=[1, 2, 3])
    context = context_cls(parent_context=parent_context)

    context.matched_update({'a_list': [4, 5, 6]})

    # The context entry is set
    assert context['a_list'] == [4, 5, 6, 1, 2, 3]

    # The parent_context entry is not modified
    assert parent_context['a_list'] == [1, 2, 3]


def test_base_context_match_update_overwrite(context_cls):
    """Tests the recursive update method for the BaseContext with the
    overwrite option."""

    # Setup the contexts
    parent_context = context_cls(a_list=[1, 2, 3])
    context = context_cls(parent_context=parent_context)

    # Do the match update. 'a_list' isn't already in the context (though it's
    # in the parent_context), so it should write it in the context
    context.matched_update({'a_list': [4, 5, 6]}, overwrite=False)

    assert context['a_list'] == [4, 5, 6, 1, 2, 3]

    # Now, trying to overwrite the entry will not do so with overwrite=False
    context.matched_update({'a_list': [7, 8, 9]}, overwrite=False)

    assert context['a_list'] == [4, 5, 6, 1, 2, 3]


def test_context_copy(context_cls):
    """Test the (shallow) copying of context classes."""

    # Setup a grand_parent, parent and child context
    grand_parent = dict(a=2, b=3, c=[])
    parent = context_cls(d=5, e=6, f=[], parent_context=grand_parent)
    child = context_cls(g=8, h=[], parent_context=parent)

    # Create a copy and check the values
    child_cp = copy.copy(child)

    # Check the parent_context and initial_valuues
    assert id(child.parent_context) == id(parent)
    assert child['_parent_context'] == child_cp['_parent_context']
    assert id(child_cp.parent_context) == id(parent)

    assert child['_initial_values'] == child_cp['_initial_values']

    assert child.keys(only_self=True) == child_cp.keys(only_self=True)
    assert child.keys() == child_cp.keys()
    assert (list(sorted(child.items(only_self=True))) ==
            list(sorted(child_cp.items(only_self=True))))
    assert list(sorted(child.items())) == list(sorted(child_cp.items()))
