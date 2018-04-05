"""
Test the Document utilities functions.
"""
from disseminate.document import Document
from disseminate.document.utils import (find_project_paths, load_root_documents,
                                        render_tree_html, translate_path)
from disseminate.utils.tests import strip_leading_space


def test_find_project_paths():
    """Test the find_project_paths function."""

    # find the project_paths
    project_paths = find_project_paths('tests')

    # Make sure the correct root paths are in the project_paths
    assert 'tests/document/example1' in project_paths
    assert 'tests/document/example2' in project_paths
    assert 'tests/document/example4/src' in project_paths

    # The following directory does not contain disseminate files and should not
    # be listed in the project_paths
    assert 'tests/document/example3' not in project_paths

    # The following directory has subdirectories. Only the root path should be
    # listed in the project_paths
    assert 'tests/document/example5' in project_paths
    assert 'tests/document/example5/sub1' not in project_paths
    assert 'tests/document/example5/sub2' not in project_paths
    assert 'tests/document/example5/sub3' not in project_paths


def test_load_root_documents(tmpdir):
    """Test the load_root_documents function"""

    # 1. load the root documents
    documents = load_root_documents('tests/document')

    # Get the src_filepaths for these documents
    src_filepaths = [d.src_filepath for d in documents]
    assert 'tests/document/example1/dummy.dm' in src_filepaths
    assert 'tests/document/example2/withheader.dm' in src_filepaths
    assert 'tests/document/example2/noheader.dm' in src_filepaths
    assert 'tests/document/example4/src/file.dm' in src_filepaths
    assert 'tests/document/example5/index.dm' in src_filepaths

    # 2. Create a srcfile in the tmpdir, render it and check the paths
    src_path = tmpdir.join('src').mkdir()
    src_filepath = src_path.join('test.dm')

    markup = """
    ---
    targets: html
    ---
    This is my first test
    """
    src_filepath.write(strip_leading_space(markup))

    documents = load_root_documents(path=str(tmpdir))

    assert len(documents) == 1
    doc = documents.pop()
    assert doc.src_filepath == str(src_filepath)

    # Render and check the destination files
    doc.render()
    assert tmpdir.join('html').join('test.html').exists()


def test_translate_path(tmpdir):
    """Test the translate_path function."""

    # 1. Load a document from example4. Example4 has a file in the 'src'
    #    directory
    target_root4 = tmpdir.join('example4')
    target_root4.mkdir()

    doc = Document('tests/document/example4/src/file.dm', str(target_root4))
    doc.render()

    # Find the document based on the src_filepath render path and relative to
    # the project root
    assert (translate_path('tests/document/example4/src/file.dm', [doc]) ==
            'tests/document/example4/src/file.dm')
    assert (translate_path('file.dm', [doc]) ==
            'tests/document/example4/src/file.dm')

    # Find the target based on the tgt_filepath relative to the target root
    # Test with and without the trailing slash
    assert (translate_path('file.html', [doc]) ==
            str(target_root4.join('html').join('file.html')))
    assert (translate_path('/file.html', [doc]) ==
            str(target_root4.join('html').join('file.html')))
    assert (translate_path('html/file.html', [doc]) ==
            str(target_root4.join('html').join('file.html')))
    assert (translate_path('/html/file.html', [doc]) ==
            str(target_root4.join('html').join('file.html')))

    # 2. Load documents from example5. Example5 has a file in the root
    #    directory, a file in the 'sub1', 'sub2' and 'sub3' directories and a
    #    file in the 'sub2/subsub2' directory
    target_root5 = tmpdir.join('example5')
    target_root5.mkdir()

    doc = Document('tests/document/example5/index.dm', str(target_root5))
    doc.render()

    # Find the documents based on src_filepath render paths
    docs = [doc]

    assert (translate_path('tests/document/example5/index.dm', docs) ==
            'tests/document/example5/index.dm')
    assert (translate_path('tests/document/example5/sub1/index.dm', docs) ==
            'tests/document/example5/sub1/index.dm')
    assert (translate_path('tests/document/example5/sub2/index.dm', docs) ==
            'tests/document/example5/sub2/index.dm')
    assert (translate_path('tests/document/example5/sub2/subsub2/index.dm',
                           docs) ==
            'tests/document/example5/sub2/subsub2/index.dm')
    assert (translate_path('tests/document/example5/sub3/index.dm', docs) ==
            'tests/document/example5/sub3/index.dm')

    # Find the documents based on src_filepaths relative to the project_root.
    assert (translate_path('index.dm', docs) ==
            'tests/document/example5/index.dm')
    assert (translate_path('sub1/index.dm', docs) ==
            'tests/document/example5/sub1/index.dm')
    assert (translate_path('sub2/index.dm', docs) ==
            'tests/document/example5/sub2/index.dm')
    assert (translate_path('sub2/subsub2/index.dm', docs) ==
            'tests/document/example5/sub2/subsub2/index.dm')
    assert (translate_path('sub3/index.dm', docs) ==
            'tests/document/example5/sub3/index.dm')

    # Find the documents based on tgt_filepath render paths.
    assert (translate_path('/index.html', docs) ==
            str(target_root5.join('html').join('index.html')))
    assert (translate_path('/sub1/index.html', docs) ==
            str(target_root5.join('html').join('sub1').join('index.html')))
    assert (translate_path('/sub2/index.html', docs) ==
            str(target_root5.join('html').join('sub2').join('index.html')))
    assert (translate_path('/sub2/subsub2/index.html', docs) ==
            str(target_root5.join('html').join('sub2').join('subsub2')
                .join('index.html')))
    assert (translate_path('/sub3/index.html', docs) ==
            str(target_root5.join('html').join('sub3').join('index.html')))

    assert (translate_path('/html/index.html', docs) ==
            str(target_root5.join('html').join('index.html')))
    assert (translate_path('/html/sub1/index.html', docs) ==
            str(target_root5.join('html').join('sub1').join('index.html')))
    assert (translate_path('/html/sub2/index.html', docs) ==
            str(target_root5.join('html').join('sub2').join('index.html')))
    assert (translate_path('/html/sub2/subsub2/index.html', docs) ==
            str(target_root5.join('html').join('sub2').join('subsub2')
                .join('index.html')))
    assert (translate_path('/html/sub3/index.html', docs) ==
            str(target_root5.join('html').join('sub3').join('index.html')))


def test_render_tree_html(tmpdir):
    """Test the render_tree_html function."""

    # Load documents from example6. The example6 directory has 2 files in the
    # 'src' directory: file1.dm, which includes file2.dm, and file2.dm. We will
    # only use file1.dm
    docs = load_root_documents('tests/document/example6')

    # Render the html for an empty docs list
    html = render_tree_html(docs[0:0])
    assert html == ''

    # Render the html for file1.dm
    html = render_tree_html(docs[0:1])
    key = """<div class="tableset">
      <table class="tablesorter" id="index">
        <thead>
          <tr>
            <th>num</th>
            <th>source</th>
            <th>targets</th>
            <th>last saved</th>
          </tr>
        </thead>
        <tr class="level-1">
          <td class="num">1</td>
          <td class="src">
            <a href="/tests/document/example6/src/file1.dm">tests/document/example6/src/file1.dm</a>
          </td>
          <td class="tgt">(<a href="file1.html">html</a>)</td>
          <td class="date">Apr 3, 2018 at 8:11PM</td>
        </tr>
        <tr class="level-2">
          <td class="num">2</td>
          <td class="src">
            <a href="/tests/document/example6/src/file2.dm">tests/document/example6/src/file2.dm</a>
          </td>
          <td class="tgt">(<a href="file2.html">html</a>)</td>
          <td class="date">Apr 3, 2018 at 8:11PM</td>
        </tr>
      </table>
    </div>
    """
    assert html == strip_leading_space(key)
