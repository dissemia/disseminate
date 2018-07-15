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
    assert context['h'] == [] and id(context['h']) == id(parent_context['h'])
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
    assert context['h'] == [] and id(context['h']) == id(parent_context['h'])
    assert 'i' not in context

    BaseContext.default_context = default_context


def test_base_context_copy():
    """Tests shallow and deep copies of the parent context and default
    context."""
    # Create a default dict and make sure that the mutables are copies and
    # not the objects themselves.
    default_context = BaseContext.default_context
    l = []
    BaseContext.default_context = {'a': l}

    context = BaseContext(b=2, c=3)
    assert 'a' in context
    assert context['a'] == []
    assert id(context['a']) != id(l)

    # But parent context objects are preserved.
    parent_context = {'a': [1,2,3]}
    context = BaseContext(parent_context=parent_context)
    assert context['a'] == [1,2,3]
    assert id(context['a']) == id(parent_context['a'])


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
    assert context.is_valid(keys=('int', 'float'))
