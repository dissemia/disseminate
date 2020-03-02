"""
Test the SequentialBuilder
"""
import logging

import pytest

from disseminate.builders.composite_builders import SequentialBuilder
from disseminate.builders.pdf2svg import Pdf2SvgCropScale
from disseminate.paths import SourcePath, TargetPath


def test_sequentialbuilder_md5decider(env, caplog, wait):
    """Test the SequentialBuilder with the Md5Decider."""
    # Track logging of DEBUG events
    caplog.set_level(logging.DEBUG)

    # We'll use the Pdf2SvgCropScale as an example of a SequentialBuilder
    assert issubclass(Pdf2SvgCropScale, SequentialBuilder)

    # 1. Test example with the infilepath and outfilepath specified that uses
    #    the PdfCrop and ScaleSvg subbuilders
    infilepath = SourcePath(project_root='tests/builders/example1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2SvgCropScale(infilepaths=infilepath, outfilepath=outfilepath,
                               env=env, crop=100, scale=2)

    assert not outfilepath.exists()  # target file not created yet

    # Run the build
    status = None
    while status != "done":
        status = pdf2svg.build()

    # Only 4 commands should have been run (pdfcrop, pdf2svg, rsvg-convert)
    # Filter logging messages for the build command
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 1

    # Make sure the intermediate files, infilepaths and outfilepath are created
    for subbuilder in pdf2svg.subbuilders:
        assert subbuilder.status == 'done'
        assert all(isinstance(i, SourcePath) for i in subbuilder.infilepaths)
        assert subbuilder.outfilepath.exists()
        assert isinstance(subbuilder.outfilepath, TargetPath)

    assert outfilepath.exists()
    mtime = outfilepath.stat().st_mtime

    # 2. Running the build again won't create a new outfilepath
    wait()  # a filesystem offset to make sure mtime can change.
    pdf2svg = Pdf2SvgCropScale(infilepaths=infilepath, outfilepath=outfilepath,
                               env=env, crop=100, scale=2)
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.stat().st_mtime == mtime

    # The commands have only been run once since the build wasn't re-done
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 1

    # This remains true even if the intermediary files are deleted
    pdf2svg.subbuilders[0].outfilepath.unlink()  # PdfCrop
    pdf2svg.subbuilders[1].outfilepath.unlink()  # Pdf2svg
    pdf2svg.subbuilders[2].outfilepath.unlink()  # ScaleSvg

    pdf2svg = Pdf2SvgCropScale(infilepaths=infilepath, outfilepath=outfilepath,
                               env=env, crop=100, scale=2)

    assert pdf2svg.status == 'done'
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.stat().st_mtime == mtime

    # The intermediary commands haven't been run again
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 1

    # 3. Changing the output file will trigger a new build
    correct_contents = outfilepath.read_bytes()
    outfilepath.write_text('wrong!')

    pdf2svg = Pdf2SvgCropScale(infilepaths=infilepath, outfilepath=outfilepath,
                               env=env, crop=100, scale=2)
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.read_bytes() == correct_contents

    # Now each commands have been run again
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 2
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 2
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 2
