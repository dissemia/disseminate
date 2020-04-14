"""
Test the SaveTempFile builder
"""
import pytest

from disseminate.builders.save_temp import SaveTempFile
from disseminate.paths import SourcePath, TargetPath


def test_save_temp_file_setup(env):
    """Test the setup of the SaveTempFile builder."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath.
    outfilepath = TargetPath(target_root=target_root, target='test',
                             subpath='subpath.test')
    save_build = SaveTempFile(env, infilepaths='my test',
                              outfilepath=outfilepath, context=context)

    # Check the paths
    assert len(save_build.infilepaths) == 1
    assert save_build.save_ext == '.test'
    assert save_build.infilepaths == ['my test']
    assert save_build.outfilepath == outfilepath

    # 2. Test an example without an outfilepath. However, a target must be
    #    specified.
    save_build = SaveTempFile(env, infilepaths='my test', save_ext='.test',
                              context=context)

    # Check the paths
    assert len(save_build.infilepaths) == 1
    assert save_build.save_ext == '.test'
    assert save_build.infilepaths == ['my test']

    assert save_build.outfilepath.target_root == env.cache_path
    assert str(save_build.outfilepath.subpath) == 'test_1488d34f91f2.test'

    # 3. Test an example with a src_filepath in the context
    context['src_filepath'] = SourcePath(project_root=env.project_root,
                                         subpath='test/test.dm')
    save_build = SaveTempFile(env, infilepaths='my test', save_ext='.test',
                              context=context)

    # Check the paths
    assert len(save_build.infilepaths) == 1
    assert save_build.save_ext == '.test'
    assert save_build.infilepaths == ['my test']

    assert save_build.outfilepath.target_root == env.cache_path
    assert str(save_build.outfilepath.subpath) == 'test/test_1488d34f91f2.test'

    # 4. Test an example without an outfilepath or target specified. An
    #    assertion error is raised
    with pytest.raises(AssertionError):
        SaveTempFile(env=env, context=context)


def test_save_temp_file_build(env):
    """Test the a simple build with the SaveTempFile builder."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath.
    outfilepath = TargetPath(target_root=target_root, target='test',
                             subpath='subpath.test')
    save_build = SaveTempFile(env, infilepaths='my test',
                              outfilepath=outfilepath, context=context)

    # Check the build
    assert save_build.status == 'ready'
    assert save_build.build() == 'done'
    assert save_build.status == 'done'

    assert save_build.outfilepath.exists()
