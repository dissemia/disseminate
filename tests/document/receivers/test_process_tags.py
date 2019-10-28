"""
Test the process_context_tags processor.
"""
from disseminate.tags import Tag
from disseminate.document.receivers import process_tags


def test_process_context_tags(doc):
    """Test the process_context_tags function."""

    header = """
    ---
    title: My @i{first} title
    author: Justin L Lorieau
    targets: html, tex
    macro: @i{example}
    ---
    This is my @macro body.
    """

    # Load the header into a context. A doc is needed with a label_manager
    # because the title tag creates a label
    context = doc.context
    context['process_context_tags'] = {'title', 'body'}
    body = context.load(header)
    context['body'] = body

    # Now process the context entries
    process_tags(context)

    # Check the entries
    assert isinstance(context['title'], Tag)
    assert context['title'].name == 'title'
    assert context['title'].content[0] == 'My '
    assert context['title'].content[1].name == 'i'
    assert context['title'].content[1].content == 'first'
    assert context['title'].content[2] == ' title'

    assert isinstance(context['author'], str)
    assert context['author'] == 'Justin L Lorieau'

    assert isinstance(context['targets'], set)
    assert context['targets'] == {'html', 'tex'}
    assert context.targets == {'.html', '.tex'}

    # The 'macro isn't listed in the 'process_context_tags' entry of the
    # context, so it isn't processed
    assert isinstance(context['macro'], str)
    assert context['macro'] == '@i{example}'

    assert isinstance(context['body'], Tag)
    assert context['body'].name == 'body'
    assert context['body'].content[0] == '    This is my '
    assert context['body'].content[1].name == 'macro'
    assert context['body'].content[2] == ' body.\n    '


def test_process_context_tags_multiple_runs(context_cls):
    """Test process_context_tags with multiple runs."""

    context = context_cls(process_context_tags=['test'],
                          test='My test')

    for i in range(3):
        process_tags(context)

    # Check that the 'test' entry was only processed once
    assert context['test'].name == 'test'
    assert context['test'].content == 'My test'
