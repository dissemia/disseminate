"""
Test features for the reports/basic template.
"""


def test_reports_basic_tag_availability(doc, wait):
    """Test the unavailability of Part tags for basic reports."""

    # 1. Write a source file and create a document
    # Write a source file and create a document
    src_filepath = doc.src_filepath

    # Part and chapter tags should not be available to reports
    for name in ('part', 'chapter'):
        wait()  # sleep time offset needed for different mtimes
        src_filepath.write_text("""
        ---
        targets: html, tex
        template: articles/basic
        ---
        @{name}{{My first {name}}}
        """.format(name=name))

        doc.build()

        # Check the rendered html. Shouldn't be rendered as an h1/h2/h3 element
        html_targetfile = doc.targets['.html']
        assert ('<span class="{name}">My first {name}</span>'.format(name=name)
                in html_targetfile.read_text())

        # Check the rendered tex. Shouldn't contain the '\part{' or '\chapter{'
        # tex command
        tex_targetfile = doc.targets['.tex']
        assert '\\{name}{{'.format(name=name) not in tex_targetfile.read_text()

    # Section, subsection and subsubsection tags should be available to reports
    for name, html in (('section',
                        '<h3 id="sec:test-dm-my-first-section">'),
                       ('subsection',
                        '<h4 id="subsec:test-dm-my-first-subsection">'),
                       ('subsubsection',
                        '<h5 id="subsubsec:test-dm-my-first-subsubsection">')
                       ):

        wait()  # sleep time offset needed for different mtimes
        src_filepath.write_text("""
        ---
        targets: html, tex
        template: articles/basic
        ---
        @{name}{{My first {name}}}
        """.format(name=name))

        doc.build()

        # Check the rendered html. Should be rendered as an h1/h2/h3 element
        html_targetfile = doc.targets['.html']
        assert html in html_targetfile.read_text()

        # Check the rendered tex. Should contain the '\section', '\subsection'
        # or '\subsubsection' tex command
        tex_targetfile = doc.targets['.tex']
        assert '\\' + name in tex_targetfile.read_text()
