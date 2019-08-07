"""
Test the functionality of the ProcessorABC base class.
"""
import pytest

from disseminate.processors import ProcessorABC


def test_processorabc_abstract_methods():
    """Test the behavior of abstract methods."""

    class Abstract(ProcessorABC):
        pass

    class Concrete(Abstract):

        # abstractmethod
        def __call__(self, *args, **kwargs):
            pass

    with pytest.raises(TypeError):
        abstract = Abstract()

    concrete = Concrete()


def test_processorabc_short_desc():
    """Test the 'short_desc' attribute of processor subclasses"""

    # Create a subclass
    class Sub(ProcessorABC):
        """This is my sub-processor.

        It has multiple paragraphs.
        """

        def __call__(self, *args, **kwargs):
            pass

    # The class's attribute is correctly set
    assert Sub.short_desc == 'This is my sub-processor.'

    # The instance attribute is correctly set
    sub = Sub()
    assert sub.short_desc == 'This is my sub-processor.'


def test_processorabc_module():
    """Test the 'module' attribute of processor subclasses"""

    # Create a subclass
    class Sub(ProcessorABC):
        """This is my sub-processor.

        It has multiple paragraphs.
        """

        def __call__(self, *args, **kwargs):
            pass

    # The class's attribute is correctly set
    assert Sub.module == 'test_processorabc'

    # The instance attribute is correctly set
    sub = Sub()
    assert sub.short_desc == 'This is my sub-processor.'


def test_processorabc_processors():
    """Test the 'processors' class method for processor subclasses."""

    class A(ProcessorABC):
        pass

    class A1(A):
        order = 500

        def __call__(self, *args, **kwargs):
            pass

    class A2(A):
        order = 100

        def __call__(self, *args, **kwargs):
            pass

    class B(ProcessorABC):
        pass

    class B1(B):
        order = 500

        def __call__(self, *args, **kwargs):
            pass

    class B2(B):
        order = 100

        def __call__(self, *args, **kwargs):
            pass

    # Try the A subclass
    processors = A.processors()
    assert len(processors) == 2
    assert isinstance(processors[0], A2)  # order 500
    assert isinstance(processors[1], A1)  # order 100

    # Try the B subclass
    processors = B.processors()
    assert len(processors) == 2
    assert isinstance(processors[0], B2)  # order 500
    assert isinstance(processors[1], B1)  # order 100
