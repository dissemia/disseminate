"""
Tests for the signals submodule.
"""
from types import MethodType

import pytest

from disseminate.signals import signal, DuplicateSignal


def test_signal():
    """Test the basic functionality of signals."""

    # Create a test receiver
    def receiver1(d):
        d['received'] = 1

    # Create a signal and register a receiver function
    test = signal('test', doc='My test signal')
    test.connect(receiver1, 100)

    assert {100} == test.receivers.keys()

    # Try emitting a signal
    d = dict()
    test.emit(d=d)
    assert d['received'] == 1

    # Now try create receivers of higher and lower order
    def receiver2(d):
        d['received'] = 2

    def receiver3(d):
        d['received'] = 3

    test.connect(receiver2, 10)
    test.connect(receiver3, 1000) # runs last, takes precedence

    assert {10, 100, 1000} == test.receivers.keys()

    test.emit(d=d)
    assert d['received'] == 3

    # Trying to connect a receiver with the same error raises an exception
    with pytest.raises(DuplicateSignal):
        test.connect(receiver3, 10)

    # Reset the signal
    test.reset()


def test_signal_decorator():
    """Test the registration of receivers using the decorator"""

    # Create a test receiver
    test = signal('test')
    @test.connect_via(1000)
    def receiver1(d):
        d['received'] = 1

    # Test emitting the signal
    d = dict()
    test.emit(d=d)

    assert 'received' in d
    assert d['received'] == 1

    test.reset()


def test_signal_method_replacement():
    """Test method replacement for signak objects."""
    # Create a test receiver
    test2 = signal('test2')
    test3 = signal('test3')

    @test2.connect_via(1000)
    def receiver1(d):
        d['received'] = 1

    @test3.connect_via(1000)
    def receiver2(d):
        d['received'] = 2

    def custom_emit(self, **kwargs):
        pass

    test2.emit = MethodType(custom_emit, test2)

    assert id(test2.emit) != id(test3.emit)

    # Make sure on the test3 signal modifies the dict
    d = dict()
    test2.emit(d=d)
    assert 'received' not in d

    test3.emit(d=d)
    assert d['received'] == 2

    test2.reset()
    test3.reset()
