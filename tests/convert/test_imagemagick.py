"""
Test for the imagemagick converters
"""
import pathlib
from disseminate import SourcePath, TargetPath
from disseminate.convert import convert


def test_tif2png(tmpdir):
    """Test the Tif2png converter."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the target file in a temp directory
    target_basefilepath = TargetPath(target_root=tmpdir,
                                     target='.png', subpath='example-1')

    # Load example tif files
    for filename in ('example-1.tif', 'example-1.tiff'):
        src_filepath = SourcePath(project_root='tests/convert/tif_example1',
                                  subpath=filename)
        target_filepath = convert(src_filepath=src_filepath,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.png'])

        # See if the file was converted
        correct_path = target_basefilepath.with_suffix('.png')
        assert target_filepath == correct_path
        assert target_filepath.is_file()
