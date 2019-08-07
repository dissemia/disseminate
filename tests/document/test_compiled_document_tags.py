"""
Test the compilation of documents with specific tags.
"""
import os

from disseminate.document import Document


def test_compiled_document_marginfig(tmpdir):
    """Test the marginfig tag in compiled documents"""

    # Create the paths in the temporary directory
    src_path = tmpdir
    src_filepath = src_path.join('main.dm')

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
        src_filepath.write(src.format(template=template))

        # Create the compiled document
        doc = Document(src_filepath=str(src_filepath),
                       target_root=str(tmpdir))
        doc.render()

        assert os.path.exists(str(tmpdir) + '/tex/main.tex')
        assert os.path.exists(str(tmpdir) + '/html/main.html')
        assert os.path.exists(str(tmpdir) + '/pdf/main.pdf')
