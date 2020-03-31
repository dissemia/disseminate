"""
Tests for the Builder find_builder_cls method.
"""
import pytest

from disseminate.builders.builder import Builder, BuildError


def test_builder_find_builder_cls():
    """Test the find_builder_cls method"""
    # The following test will require executables installed, like latexmk

    # Setup a test function
    def test_find(in_ext, out_ext, cls_name):
        builder_cls = Builder.find_builder_cls(in_ext=in_ext, out_ext=out_ext)
        assert builder_cls.__name__ == cls_name

    # 1. Test finds based on in_ext and out ext
    test_find('.tex', '.pdf', 'Latexmk')
    test_find('.pdf', '.svg', 'Pdf2SvgCropScale')
    test_find('.render', '.pdf', 'PdfRender')
    test_find('.render', '.svg', 'SvgRender')
    test_find('.*', '.*', 'Copy')
    test_find('.render', None, 'JinjaRender')

    # 2. Test based on the document target
    def test_find(in_ext, target, cls_name):
        builder_cls = Builder.find_builder_cls(in_ext=in_ext, target=target)
        assert builder_cls.__name__ == cls_name

    test_find('.css', '.html', 'Copy')
    test_find('.png', '.html', 'Copy')
    test_find('.pdf', '.html', 'Pdf2SvgCropScale')  # pdf->svg
    test_find('.render', '.html', 'SvgRender')

    test_find('.pdf', '.tex', 'Copy')
    test_find('.render', '.tex', 'PdfRender')

    # 3. Test for a document target with input files it cannot use.
    with pytest.raises(BuildError):
        Builder.find_builder_cls(in_ext='.tex', target='.html')


def test_builder_find_builder_cls_backup():
    """Test the find builder_cls method with backup builders"""

    # Setup a test function
    def test_find(in_ext, out_ext, cls_name):
        builder_cls = Builder.find_builder_cls(in_ext=in_ext, out_ext=out_ext)
        assert builder_cls.__name__ == cls_name
        return builder_cls

    # 1. Test Latexmk > Pdflatex
    latexmk = test_find('.tex', '.pdf', 'Latexmk')
    latexmk.available = False
    Builder._active.clear()
    Builder._available_builders.clear()

    test_find('.tex', '.pdf', 'Pdflatex')
    latexmk.available = True
    Builder._active.clear()
    Builder._available_builders.clear()

