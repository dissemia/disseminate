"""
Tests for the BaseContext class.
"""
import pytest

from disseminate.context import BaseContext


def test_base_context_dict():
    """Test the basic dict functionality of the base context class."""

    # initialize from kwargs
    context = BaseContext(a=1, b=2, c=3)
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


def test_base_context_default():
    """Test the utilization of the default_context."""
    default_context = BaseContext.default_context
    BaseContext.default_context = {'a': 2, 'b': 3, 'c': 4}

    context = BaseContext()
    assert len(context) >= 3
    assert context['a'] == 2
    assert context['b'] == 3
    assert context['c'] == 4

    BaseContext.default_context = default_context


def test_base_context_reset():
    """Test the reset functionality in the base context. """
    default_context = BaseContext.default_context
    BaseContext.default_context = {'a': 2, 'b': 3, 'c': 4}

    # Reset preserve the default_context, parent_context and initial values
    parent_context = {'d': 5, 'e': 6, 'h': []}
    context = BaseContext(parent_context=parent_context, f=7, g=8)
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

    # Try changing default_context, parent_context entries
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


def test_base_context_copy():
    """Tests shallow and deep copies of the parent context and default
    context."""
    # Create a default dict and make sure that the mutables are copies and
    # not the objects themselves.
    l1, l2 = [], []
    class SubContext(BaseContext):
        default_context = {'a': l1}

    # Default context mutables aren't copied
    context = SubContext(b=2, c=3, l2=l2)
    assert 'a' in context
    assert context['a'] == []
    assert id(context['a']) != id(l1)

    # Mutable initial values are copied as-is (i.e. they're shallow copies)
    assert id(context['l2']) == id(l2)

    # Parent contexts aren't copied.
    parent_context = {'l3': [1, 2, 3]}
    context = SubContext(parent_context=parent_context, l2=l2)
    assert context['l3'] == [1, 2, 3]
    assert id(context['l3']) != id(parent_context['l3'])

    # Updating the parent context mutables should update the context,
    # but updates to the context mutable should not impact the parent_context
    parent_context['l3'].append('new')
    assert context['l3'] == [1, 2, 3]  # not yet updated
    context.reset()
    assert context['l3'] == [1, 2, 3, 'new']  # updated with new parent_context
    context['l3'].append('context addition')
    assert context['l3'] == [1, 2, 3, 'new', 'context addition']
    context.reset()
    assert context['l3'] == [1, 2, 3, 'new']

    # Updates to mutables in the initial values should change the initial
    # value mutable
    context['l2'].append('l2 addition')
    assert context['l2'] == ['l2 addition']
    context.reset()
    assert context['l2'] == ['l2 addition']


def test_base_context_is_valid():
    """Tests the 'is_valid' method in the BaseContext."""
    default_validation_types = BaseContext.validation_types
    BaseContext.validation_types = {'int': int,
                                    'float': float,
                                    'str': str}

    # 1. test a context with missing entries
    context = BaseContext(b=2, c=3)
    assert not context.is_valid()

    # 2. test a context with the wrong types
    context = BaseContext(int=3.2, float=4, str=None)
    assert not context.is_valid()

    # 3. test a context with the right types, but one missing.
    context = BaseContext(int=4, float=3.2)
    assert not context.is_valid()
    assert context.is_valid(must_exist=False)

    BaseContext.validation_types = default_validation_types

    # 4. Alternatively, we could only check specific keys
    assert context.is_valid('int', 'float')

    # 5. and missing keys
    with pytest.raises(AssertionError):
        assert context.is_valid('missing')


def test_base_context_update_recursive(a_in_b):
    """Tests the recursive update method for the BaseContext."""

    # Converts a string to a dict
    context = BaseContext()
    context.recursive_update('test: one')
    assert a_in_b({'test': 'one'}, context)

    # Existing values are overwritten
    context = BaseContext(test='one')
    context.recursive_update('test: two')
    assert a_in_b({'test': 'two'}, context)

    # Types are not changed
    context = BaseContext(test=1)
    context.recursive_update('test: two')
    assert a_in_b({'test': 1}, context)

    # Unless they can be converted
    context = BaseContext(test=1)
    context.recursive_update('test: 2')
    assert a_in_b({'test': 2}, context)

    # Try a dict entry with a mismatched type
    context = BaseContext(test={'a': 1})
    context.recursive_update('test: 2')
    assert a_in_b({'test': {'a': 1}}, context)

    # Try a dict entry with a dict change
    context = BaseContext(test={'a': 1})
    context.recursive_update('test:\n  a: 2')
    assert a_in_b({'test': {'a': 2}}, context)

    context = BaseContext(test={'a': 1})
    context.recursive_update('test:\n  b: 2')
    assert a_in_b({'test': {'a': 1, 'b': '2'}}, context)

    # Try a list entry
    context = BaseContext(paths=['one', 'two'])
    context.recursive_update('paths: three')
    assert a_in_b({'paths': ['three', 'one', 'two']}, context)

    # The initial value mutables have also changed
    assert a_in_b({'_initial_values': {'paths': ['three', 'one', 'two']}},
                  context)

    # Hidden entries are not touched
    context = BaseContext(a=1)
    context.recursive_update('_initial_values:\n  b: 2')
    assert a_in_b({'_initial_values': {'a': 1}}, context)


def test_base_context_shallow_copy():
    """Test the shallow and deep copy of entries for subclasses."""

    # 1. Try subclasses with the 'shallow_copy' attributes set. This will make
    #    default_context and parent_context entries copied over as shallow
    #    copies.
    class SubContext(BaseContext):
        shallow_copy = {'l2', }

    class SubSubContext(SubContext):
        shallow_copy = {'l3', }

    l1, l2, l3 = [], [], []
    subsub_context = SubSubContext(l1=l1, l2=l2, l3=l3)

    # l1 should be a shallow copy because it is an initial value
    # l2 and l3 should be shallow copies because they were specified in the
    # 'shallow_copy' attribute
    assert id(subsub_context['l1']) == id(l1)
    assert id(subsub_context['l2']) == id(l2)
    assert id(subsub_context['l3']) == id(l3)

    # Modify the original objects
    l1.append(1)
    l2.append(2)
    l3.append(3)

    # The 'l1' entry is a shallow copy and 'l2' and 'l3' are shallow copies,
    # 'l1', 'l2' and 'l3' entries will have changed
    assert subsub_context['l1'] == [1]
    assert subsub_context['l2'] == [2]
    assert subsub_context['l3'] == [3]

    # When resetting the context, the entry for 'l1' will be a shallow
    # copy to the updated l1. The 'l2' and 'l3' entries are still shallow
    # copies of the same l2 and l3 lists.
    subsub_context.reset()
    assert subsub_context['l1'] == [1]
    assert subsub_context['l2'] == [2]
    assert subsub_context['l3'] == [3]

    # Modifying the lists will still change the originals
    subsub_context['l1'].append('a')
    subsub_context['l2'].append('b')
    subsub_context['l3'].append('c')

    assert l1 == [1, 'a']
    assert l2 == [2, 'b']
    assert l3 == [3, 'c']

    # 2. Try subclasses without the 'shallow_copy' attributes set. This will
    #    make default_context and parent_context entries copied over as deep
    #    copies.
    class SubContext(BaseContext):
        pass

    class SubSubContext(SubContext):
        pass

    # Create a new SubSubContext object, but now place l2 and l3 in the parent
    # context. These will now be deep copies.
    l1, l2, l3 = [], [], []
    subsub_context = SubSubContext(l1=l1, parent_context={'l2': l2, 'l3': l3})

    # l1 should be a shallow copy because it is an initial value
    # l2 and l3 should be deep copies because they were not specified in the
    # 'shallow_copy' attribute
    assert id(subsub_context['l1']) == id(l1)
    assert id(subsub_context['l2']) != id(l2)
    assert id(subsub_context['l3']) != id(l3)

    # Modify the original objects
    l1.append(1)
    l2.append(2)
    l3.append(3)

    # Since the 'l1' entry is a shallow copy and 'l2' and 'l3' are deep copies,
    # only 'l1' will have changed
    assert subsub_context['l1'] == [1]
    assert subsub_context['l2'] == []
    assert subsub_context['l3'] == []

    # When resetting the context, the entry for 'l1' will be a shallow
    # copy to the updated l1. The 'l2' and 'l3' entries become deep copies of
    # the modified l2 and l3.
    subsub_context.reset()
    assert subsub_context['l1'] == [1]
    assert subsub_context['l2'] == [2]
    assert subsub_context['l3'] == [3]

    # Modifying the lists will only change l1
    subsub_context['l1'].append('a')
    subsub_context['l2'].append('b')
    subsub_context['l3'].append('c')

    assert l1 == [1, 'a']
    assert l2 == [2]
    assert l3 == [3]
