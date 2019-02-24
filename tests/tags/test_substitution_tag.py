"""
Test the substitution tag.
"""
from disseminate.tags.substitution import Substitution
from disseminate.ast import process_context_asts
from disseminate.paths import SourcePath


def test_substitution_basic(context_cls):
    """Basic tests for the behavior of the substitution tag."""

    context = context_cls()
    sub = Substitution(name='test', content='invalid', attributes=(),
                       context=context)

    # The content should have been ignored
    assert sub.content == ''

    # Now place a value in the context to substitute
    context['test'] = 'my test'

    # The content should now be replaced
    assert sub.content == ''
    assert sub.txt == 'my test'


def test_substitution_multiple(context_cls):
    """Test the multiple substitution of macros."""

    context = context_cls(**{'p90x': '90@deg@sub{x}',
                             'deg': '°',
                             'body': 'This is my @p90x pulse',
                             'src_filepath': SourcePath('src')})

    # Process the entries in the context
    process_context_asts(context=context)
    print(context['p90x'])
    assert context['body'].txt == 'This is my 90°x pulse'

