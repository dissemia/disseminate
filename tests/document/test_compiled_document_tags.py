"""
Test the compilation of documents with specific tags.
"""
from disseminate.document import CompiledDocument


def test_compiled_document_marginfig(tmpdir):
    """Test the marginfig tag in compiled documents"""

    # Create the paths in the temporary directory
    src_path = tmpdir
    src_filepath = src_path.join('main.dm')
    src_file = src_filepath.join('main.dm')
    targets = {k: str(tmpdir.join(k.strip('.')).join('main' + k)) for k in
               ('.html', '.tex', '.pdf')}

    # Create the source for the template
    src = """
        ---
        template: {template}
        ---
        This is my @marginfig{{Margin figure}}.
        """

    # For each template type try rendering the fiel
    for template in ('template', 'tufte',):
        # Write the source
        src_filepath.write(src.format(template=template))
        print(src.format(template=template))
        # Create the compiled document
        doc = CompiledDocument(src_filepath=str(src_filepath),
                               targets=targets, global_context=None)
        doc.render()
