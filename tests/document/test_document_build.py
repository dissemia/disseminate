"""
Tests document build and build_needed methods.
"""
from pathlib import Path

# Setup example paths
ex8_root = Path("tests") / "document" / "examples" / "ex8"


def test_document_simple_pdf(env, is_pdf, wait):
    """Tests the compilation of a simple pdf file."""

    # Create a src document
    doc = env.root_document
    target_root = doc.target_root
    src_filepath = doc.src_filepath

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    This is my first document""")

    # reload the file
    doc.load()

    # Make sure the target PDF hasn't been created yet.
    assert not doc.targets['.pdf'].is_file()

    # build the document
    assert doc.build_needed()
    assert doc.build() == 'done'
    assert not doc.build_needed()

    # See if the PDF was succesfully generated (and the tex file is not in
    # the target directories; it should be in a cache directory)
    assert (target_root / 'pdf' / 'test.pdf').is_file()
    assert not (target_root / 'pdf' / 'test.tex').is_file()
    assert not (target_root / 'tex' / 'test.tex').is_file()
    assert is_pdf(doc.targets['.pdf'])

    # Make sure rendering again will not generate a new file
    st_mtime = doc.targets['.pdf'].stat().st_mtime
    wait()  # sleep time offset needed for different mtimes

    assert doc.build() == 'done'  # PdfBuilder successful
    assert doc.targets['.pdf'].stat().st_mtime == st_mtime

    # Now change the src tex file and make sure the pdf has changed
    wait()  # sleep time offset needed for different mtimes
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    new""")

    # Render again, and the mtime should change
    assert doc.build() == 'done'  # PdfBuilder successful
    assert doc.targets['.pdf'].stat().st_mtime != st_mtime


def test_document_simple_tex_pdf(env, is_pdf):
    """Tests the compilation of simple tex and pdf files.
    """

    # Create a src document
    doc = env.root_document
    target_root = doc.target_root
    src_filepath = doc.src_filepath

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: tex, pdf
    ---
    This is my third document""")

    # Render the document
    assert doc.build_needed()
    assert doc.build() == 'done'  # PdfBuilder, TexBuilder successful
    assert not doc.build_needed()

    # See if the tex and pdf files were succesfully generated
    assert (target_root / 'pdf' / 'test.pdf').is_file()
    assert not (target_root / 'pdf' / 'test.tex').is_file()
    assert (target_root / 'tex' / 'test.tex').is_file()
    assert is_pdf(doc.targets['.pdf'])


def test_document_template_books_tufte(load_example):
    """Test rendering in html, tex, pdf for the books/tufte template.
    (examples/ex8)
    """
    # Load the document with equations (@eq) an asymptote (@asy) tags
    # 1. See how a subdocument alone is rendered
    doc = load_example(ex8_root / "src" / "fundamental_solnNMR" /
                       "inept" / "inept.dm")
    target_root = doc.target_root

    # Check modifications from the context.txt (books/tufte)
    assert doc.context['template'] == 'books/tufte'
    assert 'heading_chapter_html' in doc.context['label_fmts']
    assert (doc.context['label_fmts']['heading_chapter_html'] ==
            "@prefix{@label.chapter_number} @label.title")

    # Render the document
    assert doc.build_needed()
    assert doc.build() == 'done'
    assert not doc.build_needed()

    # Check the dependencies and paths
    html_root = target_root / 'html'
    html_key = {html_root / 'media',  # dirs
                html_root / 'media' / 'css',

                html_root / 'inept.html',  # files
                html_root / 'media' / 'eq_6b1a39e86f33.svg',
                html_root / 'media' / 'eq_95cdf31980fa.svg',
                html_root / 'media' / 'eq_d98b71da63d9.svg',
                html_root / 'media' / 'inept_599eeae484a5.svg',
                html_root / 'media' / 'css' / 'base.css',
                html_root / 'media' / 'css' / 'bootstrap.min.css',
                html_root / 'media' / 'css' / 'default.css',
                html_root / 'media' / 'css' / 'pygments.css',
                html_root / 'media' / 'css' / 'tufte.css',
                }
    html_actual = set(html_root.glob('**/*'))
    assert html_key == html_actual

    tex_root = target_root / 'tex'
    tex_key = {tex_root / 'media',  # dirs

               tex_root / 'inept.tex',  # files
               tex_root / 'media' / 'inept_599eeae484a5.pdf',
               }
    tex_actual = set(tex_root.glob('**/*'))
    assert tex_key == tex_actual

    pdf_root = target_root / 'pdf'
    pdf_key = {pdf_root / 'inept.pdf',
               }
    pdf_actual = set(pdf_root.glob('**/*'))
    assert pdf_key == pdf_actual

    # Check the rendered html
    key = (ex8_root / "html" / "inept.html").read_text()
    print(doc.targets['.html'])
    assert doc.targets['.html'].read_text() == key
