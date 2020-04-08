"""
Test the compilation of documents with specific tags.
"""

def test_compiled_document_marginfig(env):
    """Test the marginfig tag in compiled documents"""

    # Create the paths in the temporary directory
    doc = env.root_document
    src_filepath = doc.src_filepath

    # Create the source for the template
    src = """
        ---
        template: {template}
        targets: html, tex, pdf
        ---
        This is my @marginfig{{Margin figure}}.
        """

    # For each template type try rendering the field
    for template in ('default', 'books/tufte',):
        # Write the source
        src_filepath.write_text(src.format(template=template))

        # Reload and render the document
        doc.render()

        assert doc.targets['.tex'].is_file()
        assert doc.targets['.html'].is_file()
        assert doc.targets['.pdf'].is_file()
