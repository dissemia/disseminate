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
    assert sub.content == 'my test'
    assert sub.txt == 'my test'


def test_substitution_multiple(context_cls):
    """Test the multiple substitution of macros."""

    context = context_cls(**{'p90x': '90@deg@sub{x}',
                             'deg': '°',
                             'body': 'This is my @p90x pulse',
                             'src_filepath': SourcePath('src')})

    # Process the entries in the context
    process_context_asts(context=context)

    # Test basic subsitution using the .txt target to strip tags
    assert context['body'].txt == 'This is my 90°x pulse'

    # Test basic substitution using the .html target.
    assert context['body'].html == ('<span class="body">'
                                    'This is my '
                                    '<span class="p90x">90&#176;'
                                    '<sub>x</sub></span> '
                                    'pulse</span>\n')

    # Test basic substitution using the .tex target.
    assert context['body'].tex == r'This is my 90°\ensuremath{_{x}} pulse'


def test_substitution_case_sensitive(context_cls):
    """Ensure that substitutions are case sensitive."""

    context = context_cls(**{'case': 'case',
                             'CASE': 'CASE',
                             '13c': '13c',
                             '13C': '13C',
                             'src_filepath': SourcePath('src')})

    test = 'This is my lower @case and upper @CASE. Lower @13c and upper @13C.'
    context['body'] = test

    # Process the entries in the context
    process_context_asts(context=context)

    #  Test basic subsitution using the .txt target to strip tags
    assert context['body'].txt == ('This is my lower case and upper CASE. '
                                   'Lower 13c and upper 13C.')
