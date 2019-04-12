"""
Test the process_header processors.
"""
from pathlib import Path

import disseminate.processors as pr


def test_process_header(context_cls):
    """Test the process_context_header function."""

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
    """Test the process_context_header function when types need to be
    matched."""

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


def test_process_context_additional_header_files(tmpdir, context_cls):
    """Test the process_context_additional_header_files function."""

    tmpdir = Path(tmpdir)

    # Create temp paths
    paths = [tmpdir / 'sub1', tmpdir / 'sub2']
    [p.mkdir() for p in paths]

    # 1. Try basic value entries
    # Create a basic parent_context and context, including values needed by
    # process_context_additional_header_files

    parent_context = context_cls(value='a',
                                 additional_header_filename='context.txt',
                                 paths=paths)
    context = context_cls(parent_context=parent_context)

    # Value is accessed from the parent context
    assert context['value'] == 'a'

    # Create additional headers and see how they're read in
    header1 = tmpdir / 'sub1' / 'context.txt'
    header1.write_text("value: b")

    header2 = tmpdir / 'sub2' / 'context.txt'
    header2.write_text("value: c")

    # Try the processor
    processor = pr.process_context_headers.ProcessContextAdditionalHeaderFiles()
    processor(context)

    # Since header1 is the first in the path, its value gets loaded locally
    # into the context, but the value from header2 is not overwritten.
    # Consequently, 'value' should equal 'b'. The parent_context's value should
    # still be 'a'
    assert context['value'] == 'b'
    assert parent_context['value'] == 'a'

    # 2. Try nested values
    parent_context = context_cls(value={'nested': 'a'},
                                 additional_header_filename='context.txt',
                                 paths=paths)
    context = context_cls(parent_context=parent_context)

    # Value is accessed from the parent context
    assert context['value'] == {'nested': 'a'}

    # Create additional headers and see how they're read in
    header1 = tmpdir / 'sub1' / 'context.txt'
    header1.write_text("value:\n  nested: b")

    header2 = tmpdir / 'sub2' / 'context.txt'
    header2.write_text("value:\n  nested: c")

    # Try the processor
    processor = pr.process_context_headers.ProcessContextAdditionalHeaderFiles()
    processor(context)

    # Since header1 is the first in the path, its value gets loaded locally
    # into the context, but the value from header2 is not overwritten.
    # Consequently, 'value' should equal 'b'. The parent_context's value should
    # still be 'a'
    assert context['value'] == {'nested': 'b'}
    assert parent_context['value'] == {'nested': 'a'}

    # 3. Try mutables, like lists
    parent_context = context_cls(value=['a'],
                                 additional_header_filename='context.txt',
                                 paths=paths)
    context = context_cls(parent_context=parent_context)

    # Value is accessed from the parent context
    assert context['value'] == ['a']

    # Create additional headers and see how they're read in
    header1 = tmpdir / 'sub1' / 'context.txt'
    header1.write_text("value: b")

    header2 = tmpdir / 'sub2' / 'context.txt'
    header2.write_text("value: c")

    # Try the processor
    processor = pr.process_context_headers.ProcessContextAdditionalHeaderFiles()
    processor(context)

    # Since header1 is the first in the path, its value gets loaded locally
    # into the context, but the value from header2 is not overwritten.
    # Consequently, 'value' should equal 'b'. The parent_context's value should
    # still be 'a'
    assert context['value'] == ['b', 'a']
    assert parent_context['value'] == ['a']
