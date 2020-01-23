"""
Test the BaseRenderer functions and classes.
"""
from disseminate.renderers import BaseRenderer
from disseminate.renderers.utils import load_renderers


def test_load_renderers(doc):
    """Test the load_renderers function."""

    context = doc.context
    context['targets'] = {'.tex'}
    # Test the proper creation of renderers in the DocumentContext
    load_renderers(context)

    assert 'renderers' in context
    assert isinstance(context['renderers'], dict)
    assert 'template' in context['renderers']

    renderer = context['renderers']['template']
    assert isinstance(renderer, BaseRenderer)
    assert issubclass(renderer.__class__, BaseRenderer)
    assert renderer.targets == {'.tex'}

    doc.load()
    assert renderer.targets == {'.tex'}
