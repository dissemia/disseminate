"""
Test the process_header processors.
"""
import disseminate.processors as pr


def test_process_header(context_cls):
    """Test the process_header function."""

    header = """
    ---
    title: My @i{first} title
    author: Justin L Lorieau
    targets: html, tex
    macro: @i{example}
    ---
    This is my @macro body.
    """

    # Load the header into a context
    context = context_cls(test=header)

    # Now process the context entries
    processor = pr.process_context_headers.ProcessContextHeaders()
    processor(context)

    # Ensure that the 'test' entry's header was parsed
    assert context['test'] == '    This is my @macro body.\n    '
    assert context['title'] == 'My @i{first} title'
    assert context['author'] == 'Justin L Lorieau'
    assert context['targets'] == 'html, tex'
    assert context['macro'] == '@i{example}'


def test_process_header_with_type_match(context_cls):
    """Test the process_header function when types need to be matched."""

    header = """
    ---
    targets: html, tex
    ---
    My body
    """

    # Load the header into a context
    context = context_cls(test=header, targets=[])

    # Now process the context entries
    processor = pr.process_context_headers.ProcessContextHeaders()
    processor(context)

    # Ensure that the 'test' entry's header was parsed
    assert context['test'] == '    My body\n    '

    # The targets entry should have been converted to a list because the
    # context was created with a targets entry with a list as its value.
    assert context['targets'] == ['html', 'tex']
