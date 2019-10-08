"""
Test the process_header processors.
"""
import disseminate.document.processors as pr
from disseminate import settings


def test_process_context_header(context_cls):
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

    # Setup a context class with a targets attribute
    class SubContext(context_cls):
        targets = ['.html']
        preload = {'targets', 'renderers', 'template'}

    # Load the header into a context
    context = SubContext(test=header)

    # Now process the context entries
    processor = pr.process_context_headers.ProcessContextHeaders()
    processor(context)

    # Ensure that the 'test' entry's header was parsed
    assert context['test'] == '    This is my @macro body.\n    '
    assert context['title'] == 'My @i{first} title'
    assert context['author'] == 'Justin L Lorieau'
    assert context['targets'] == 'html, tex'
    assert context['macro'] == '@i{example}'


def test_process_context_header_custom_template(doc):
    """Test the process_context_header loading of custom templates."""

    project_root = doc.project_root
    template_filepath = project_root / 'mytemplate.html'
    template_filepath.touch()

    doc.context['template'] = 'mytemplate'

    # Try the processor
    processor = pr.process_context_headers.ProcessContextHeaders()
    processor(doc.context)

    # Make sure the custom template was read in
    assert 'renderers' in doc.context
    assert 'template' in doc.context['renderers']
    assert doc.context['renderers']['template'].template == 'mytemplate'


def test_process_context_header_additional_context_files(doc):
    """Test the process_context_header with additional context files."""

    # 1. Try basic value entries
    # Create a basic parent_context and context, including values needed by
    # process_context_additional_header_files
    assert 'value' not in doc.context

    # Create additional headers and see how they're read in. These are tied
    # to templates, so create a template as well
    project_root = doc.project_root

    header1 = project_root / 'context.txt'
    template_filepath = project_root / 'mytemplate.html'

    header1.write_text("value: b")
    template_filepath.touch()

    doc.context['template'] = 'mytemplate'

    # Try the processor
    processor = pr.process_context_headers.ProcessContextHeaders()
    processor(doc.context)

    # Since header1 is the first in the path, its value gets loaded locally
    # into the context, but the value from header2 is not overwritten.
    # Consequently, 'value' should equal 'b'. The parent_context's value should
    # still be 'a'
    assert doc.context['value'] == 'b'


def test_process_context_header_precedence(doctree, wait):
    """Test the precedence of context entries between the default context,
    template context and document context."""

    # Load the 3 documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list()

    # 1. Initially, these documents should have default context entries from
    #    the default context (settings) and the default template
    #    (templates/default/context.txt). Updating the default template's
    #    context may require updating this test.
    for doc in (doc1, doc2, doc3):
        assert 'attr' not in doc.context
        assert doc.context['inactive_tags'] == {'sidenote'}
        assert doc.context['template'] == 'default/template'

    # 2. Add a template with a context.txt
    wait()  # sleep time offset needed for different mtimes
    src_path = doc1.src_filepath.parent
    template_filepath = src_path / 'test.html'
    context_filepath = src_path / 'context.txt'

    template_filepath.write_text("""
    <html>
    </html>
    """)
    context_filepath.write_text("""
    inactive_tags: chapter
    attr: string
    """)
    doc1.src_filepath.write_text("""
    ---
    template: test
    ---
    """)
    for doc in (doc1, doc2, doc3):
        doc.load()

    assert doc1.context['template'] == 'test'
    assert doc1.context['inactive_tags'] == {'chapter'}
    assert doc2.context['inactive_tags'] == {'chapter'}
    assert doc3.context['inactive_tags'] == {'chapter'}
    assert doc1.context['attr'] == 'string'
    assert doc2.context['attr'] == 'string'
    assert doc3.context['attr'] == 'string'

    # 3. Now write the attribute in the root document (doc1) and it should
    #    override the value for the document and subdocuments
    wait()  # sleep time offset needed for different mtimes
    doc1.src_filepath.write_text("""
    ---
    template: test
    inactive_tags: title
    attr: new string
    ---
    """)
    for doc in (doc1, doc2, doc3):
        doc.load()

    assert doc1.context['inactive_tags'] == {'title'}  # replaced
    assert doc2.context['inactive_tags'] == {'title'}
    assert doc3.context['inactive_tags'] == {'title'}
    assert doc1.context['attr'] == 'new string'  # replaced
    assert doc2.context['attr'] == 'new string'
    assert doc3.context['attr'] == 'new string'



