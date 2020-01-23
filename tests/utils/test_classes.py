"""
Test classes utility functions.
"""
from disseminate.utils.classes import weakattr


def test_weakattrs():
    """Test weakref attributes."""

    # Create test classes

    # attributes 'a' and 'b' contain weakrefs to objects
    class Test(object):
        a = weakattr()
        b = weakattr()

    class SubTest(Test):
        b = weakattr()
        c = weakattr()

    # Create a class from the base Test class
    test1 = Test()
    test2 = Test()

    test1.a = test2
    test1.b = Test()
    test1.c = 1

    assert (i in test1.__dict__['__weakrefattr__'] for i in ['a', 'b'])

    assert test1.a == test2
    assert test1.b is None  # Dead link
    assert test1.c == 1

    # Test deleting an attribute
    del test1.a
    assert test1.a is None
    assert test2 is not None

    # Try removing an object
    del test2
    assert test1.b is None  # Dead link

    # Now try with the subclass
    subtest1 = SubTest()
    subtest2 = SubTest()

    subtest1.a = subtest2
    subtest1.b = SubTest()
    subtest1.c = subtest2

    assert (i in test1.__dict__['__weakrefattr__'] for i in ['a', 'b', 'c'])

    assert subtest1.a == subtest2
    assert subtest1.b is None  # Dead link
    assert subtest1.c == subtest2

    del subtest2
    assert subtest1.a is None
    assert subtest1.c is None
