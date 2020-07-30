"""
Test the SaveTempFile builder
"""
import pytest

from disseminate.builders.save_temp import SaveTempFile
from disseminate.paths import SourcePath, TargetPath


def test_save_temp_file_with_find_builder_cls():
    """Test the SaveTempFile builder access with the find_builder_cls."""

    builder_cls = SaveTempFile.find_builder_cls(in_ext='.save')
    assert builder_cls.__name__ == "SaveTempFile"


def test_save_temp_file_setup_with_outfilepath(env):
    """Test the setup of the SaveTempFile builder with an outfilepath
    specified."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath.
    outfilepath = TargetPath(target_root=target_root, target='test',
                             subpath='subpath.test')
    save_build = SaveTempFile(env, parameters='my test',
                              outfilepath=outfilepath, context=context)

    # Check the paths
    assert len(save_build.parameters) == 1
    assert save_build.infilepath_ext == '.test'
    assert save_build.parameters == ['my test']
    assert save_build.outfilepath == outfilepath


def test_save_temp_file_setup_without_outfilepath(env):
    """Test the setup of the SaveTempFile builder without an outfilepath
    specified."""
    context = env.context
    target_root = context['target_root']

    # 2. Test an example without an outfilepath. However, a target must be
    #    specified.
    save_build = SaveTempFile(env, parameters='my test', save_ext='.test',
                              context=context)

    # Check the paths
    assert len(save_build.parameters) == 1
    assert save_build.infilepath_ext == '.test'
    assert save_build.parameters == ['my test']

    assert (save_build.outfilepath ==
            env.target_root / 'media' / 'test_1488d34f91f2.test')

    # 3. Test an example with a src_filepath in the context
    context['src_filepath'] = SourcePath(project_root=env.project_root,
                                         subpath='test/test.dm')
    save_build = SaveTempFile(env, parameters='my test', save_ext='.test',
                              context=context)

    # Check the paths
    assert len(save_build.parameters) == 1
    assert save_build.infilepath_ext == '.test'
    assert save_build.parameters == ['my test']

    assert (save_build.outfilepath ==
            env.target_root / 'media' / 'test/test_1488d34f91f2.test')


def test_save_temp_file_build(env):
    """Test the a simple build with the SaveTempFile builder."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath.
    outfilepath = TargetPath(target_root=target_root, target='test',
                             subpath='subpath.test')
    save_build = SaveTempFile(env, parameters='my test',
                              outfilepath=outfilepath, context=context)

    # Check the build
    assert save_build.status == 'ready'
    assert save_build.build() == 'done'
    assert save_build.status == 'done'

    assert save_build.outfilepath.exists()
