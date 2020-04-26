"""
Tests for builders based on ImageMagick.
"""
from disseminate.builders.imagemagick import Tif2png, Tiff2png
from disseminate.paths import SourcePath, TargetPath


def test_tif2png_with_find_builder_cls():
    """Test the Tif2png builder access with the find_builder_cls."""

    builder_cls = Tif2png.find_builder_cls(in_ext='.tif', out_ext='.png')
    assert builder_cls.__name__ == "Tif2png"

    builder_cls = Tif2png.find_builder_cls(in_ext='.tiff', out_ext='.png')
    assert builder_cls.__name__ == "Tiff2png"


def test_tif2png(env):
    """Test the Tif2Png and Tiff2Png builders."""
    # Make sure these builders are active
    assert Tif2png.active
    assert Tiff2png.active

    # 1. Try a conversions (.tif -> .png)
    infilepath = SourcePath('tests/builders/examples/ex2', 'example-1.tif')
    cache_path = TargetPath(env.cache_path, 'media/example-1.png')

    tif2png = Tif2png(env, parameters=infilepath)

    assert tif2png.status == 'ready'
    assert tif2png.outfilepath == cache_path
    assert not tif2png.outfilepath.exists()

    # Build
    assert tif2png.build(complete=True) == 'done'
    assert tif2png.status == 'done'
    assert tif2png.outfilepath.exists()

    # 2. Try a conversion. (.tiff -> .png)
    #    This build won't be needed because the source file and target files
    #    are the same.
    infilepath = SourcePath('tests/builders/examples/ex2', 'example-1.tiff')
    tiff2png = Tiff2png(env, parameters=infilepath)

    assert tiff2png.status == 'done'
