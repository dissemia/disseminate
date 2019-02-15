"""
Test the Ref tag.
"""
import pathlib

import pytest

from disseminate import Document, SourcePath, TargetPath
from disseminate.ast import process_ast
from disseminate.labels import LabelNotFound


def test_ref_missing(tmpdir):
    """Test the ref tag for a missing caption"""
    # Create a temporary document
    src_path = pathlib.Path(tmpdir, 'src')
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='main.dm')
    src_filepath.touch()
    target_root = TargetPath(tmpdir)

    doc = Document(src_filepath=src_filepath, target_root=target_root)
    doc.context['caption_figure'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@ref{test} @caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Trying to convert the root ast to a target type, like html, will raise
    # an LabelNotFound error
    with pytest.raises(LabelNotFound):
        root.html

    # There should be only one label for the document
    assert len(label_man.labels) == 1
    assert len(label_man.get_labels(kinds='document')) == 1


# html tests

def test_ref_html(tmpdir):
    """Test the ref tag for a present caption in the html format"""
    # Create a temporary document
    src_path = pathlib.Path(tmpdir, 'src')
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='main.dm')
    src_filepath.touch()
    target_root = TargetPath(tmpdir)

    doc = Document(src_filepath=src_filepath, target_root=target_root)
    doc.context['label_fmts']['ref_figure_html'] = ('@a[href="$link"]{'
                                                    'Fig. $label.number}')
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup with an id. The marginfig tag is needed to
    # set the kind of the label.
    src = "@ref{test} @marginfig{@caption[id=test]{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    #  Test the ref's html
    root_html = root.html

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    key = '<a href="/html/main.html#test">Fig. 1</a>'

    assert key in root_html


# tex tests

def test_ref_tex(tmpdir):
    """Test the ref tag for a present caption in the texformat"""
    # Create a temporary document
    src_path = pathlib.Path(tmpdir, 'src')
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='main.dm')
    src_filepath.touch()
    target_root = TargetPath(tmpdir)

    doc = Document(src_filepath=src_filepath, target_root=target_root)
    label_man = doc.context['label_manager']

    doc.context['label_fmts']['ref_figure_tex'] = ("\\hyperref[$label.id]{"
                                                   "Fig. $label.number}")
    doc.context['targets'] = '.tex'

    # Generate the markup without an id. A reference cannot be made, and a
    # LabelNotFound exception is raised
    src = "@ref{test} @marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Rendering the tex raises the LabelNotFound exception since the label
    # with id 'test' wasn't defined.
    with pytest.raises(LabelNotFound):
        root.tex

    # Generate the markup with an id. The marginfig tag is needed to
    # set the kind of the label.
    src = "@ref{test} @marginfig{@caption[id=test]{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    #  Test the ref's html
    root_tex = root.tex
    assert root_tex.startswith('\\hyperref[test]{Fig. 1}')
