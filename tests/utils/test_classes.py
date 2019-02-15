"""
Test classes utility functions.
"""
from disseminate.utils.classes import weakattr, trackmtimes


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


def test_trackmtimes():
    """Test the @trackmtimes class wrapper."""

    # Test include attributes
    @trackmtimes(includeattrs=('a'))
    class Test1(object):
        pass

    # Test exclude attributes
    @trackmtimes(excludeattrs=('b'))
    class Test2(object):
        pass

    for test_cls in (Test1, Test2):
        # Changing the value after setting the initial value will update the
        # mtime only for attribute 'a'
        test = test_cls()
        assert not hasattr(test, 'mtime')  # mtime not set, since no attrs
                                           # changed
        test.b = 2  # 'b' isn't tracked for mtimes
        assert not hasattr(test, 'mtime')
        test.b = 3  # changes to 'b' doesn't set the mtime
        assert not hasattr(test, 'mtime')

        # After setting 'a', changes to 'a' will set the mtime
        test.a = 1
        assert not hasattr(test, 'mtime')
        test.a = 2
        assert hasattr(test, 'mtime') and isinstance(test.mtime, float)

        # Check to make sure the mtime is getting updated
        mtime = test.mtime
        test.a = 2
        assert test.mtime == mtime
        test.a = 3
        assert test.mtime > mtime

    # Test subclassing with exclude attrs
    @trackmtimes(excludeattrs=('a'))
    class Test(object):
        pass

    class SubTest(Test):
        pass

    # The behavior of Test and SubTest should be the same
    for test_cls in (Test, SubTest):
        # Create the object and instantiate with initial values. This does not
        # set the modification times
        test = test_cls()
        test.a = 1
        test.b = 2
        test.c = 3

        assert test._trackmtimes_excludes_ == {'a'}
        assert not hasattr(test, 'mtime')
        test.a = 2
        assert not hasattr(test, 'mtime')
        test.b = 3
        assert hasattr(test, 'mtime')
        mtime = test.mtime
        test.c = 4
        assert test.mtime > mtime

    # Test subclass with include attrs
    @trackmtimes(includeattrs=('a'))
    class Test(object):
        pass

    @trackmtimes(includeattrs=('b'))
    class SubTest(Test):
        pass

    # Create the object and instantiate with initial values. This does not
    # set the modification times
    test = Test()
    test.a = 1
    test.b = 2

    # Only changes to 'a' produce mtime changes
    assert test._trackmtimes_includes_ == {'a'}
    assert test._trackmtimes_excludes_ == set()
    assert not hasattr(test, 'mtime')
    test.b = 3
    assert not hasattr(test, 'mtime')
    test.a = 2
    assert hasattr(test, 'mtime')

    # Now with SubTest, attributes 'a' and 'b' will change the mtime.
    test = SubTest()
    test.a = 1
    test.b = 2

    # Only changes to 'a' produce mtime changes
    assert test._trackmtimes_includes_ == {'a', 'b'}
    assert test._trackmtimes_excludes_ == set()
    assert not hasattr(test, 'mtime')
    test.a = 2
    assert hasattr(test, 'mtime')
    mtime = test.mtime
    test.b = 3
    assert mtime < test.mtime  # updated mtime

    # Test mtime properties
    @trackmtimes(includeattrs=('a'))
    class Test(object):
        @property
        def mtime(self):
            return getattr(self, '_mtime', None)

        @mtime.setter
        def mtime(self, value):
            setattr(self, '_mtime', value)

    test = Test()

    assert test.mtime is None
    test.a = 1
    assert test.mtime is None
    test.a = 2
    assert test.mtime is not None
