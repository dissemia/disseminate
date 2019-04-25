"""
Test features for the reports/basic template.
"""
from disseminate.document import Document
from disseminate.paths import SourcePath, TargetPath


def test_reports_basic_tag_availability(tmpdir):
    """Test the unavailability of Part tags for basic reports."""

    # 1. Write a source file and create a document
    # Write a source file and create a document
    src_filepath = SourcePath(project_root=tmpdir, subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)

    # Part and chapter tags should not be available to reports
    for name in ('part', 'chapter'):
        src_filepath.write_text("""
        ---
        targets: html, tex
        template: reports/basic
        ---
        @{name}{{My first {name}}}
        """.format(name=name))

        doc = Document(src_filepath=src_filepath, target_root=target_root)
        doc.render()

        # Check the rendered html. Shouldn't be rendered as an h1/h2/h3 element
        html_targetfile = doc.targets['.html']
        assert ('<span class="{name}">My first {name}</span>'.format(name=name)
                in html_targetfile.read_text())

        # Check the rendered tex. Shouldn't contain the '\part' or '\chapter'
        # tex command
        tex_targetfile = doc.targets['.tex']
        assert '\\' + name not in tex_targetfile.read_text()

    # Section, subsection and subsubsection tags should be available to reports
    for name, html in (('section',
                        '<h3 id="sec:test-dm-my-first-section">'),
                       ('subsection',
                        '<h4 id="subsec:test-dm-my-first-subsection">'),
                        ('subsubsection',
                         '<h5 id="subsubsec:test-dm-my-first-subsubsection">'),
                       ):
        src_filepath.write_text("""
        ---
        targets: html, tex
        template: reports/basic
        ---
        @{name}{{My first {name}}}
        """.format(name=name))

        doc = Document(src_filepath=src_filepath, target_root=target_root)
        doc.render()

        # Check the rendered html. Should be rendered as an h1/h2/h3 element
        html_targetfile = doc.targets['.html']
        assert html in html_targetfile.read_text()

        # Check the rendered tex. Should contain the '\section', '\subsection'
        # or '\subsubsection' tex command
        tex_targetfile = doc.targets['.tex']
        assert '\\' + name in tex_targetfile.read_text()
