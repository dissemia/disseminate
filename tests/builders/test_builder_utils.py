"""
Test utils for builders
"""
from disseminate.builders.utils import (generate_mock_infilepath,
                                        generate_outfilepath)
from disseminate.paths import SourcePath, TargetPath


def test_generate_mock_infilepath(env):
    """Test the generate_mock_infilepath function."""

    # 1. Test examples with simple strings
    fp = generate_mock_infilepath(env=env, infilepaths='test_text', ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == '35862287bc72.test'

    # 2. Test examples with other source files
    # 2.1. Test an example with an infilepath in the infilepaths
    infilepath = SourcePath(project_root='test', subpath='mytest.html')
    fp = generate_mock_infilepath(env=env, infilepaths=[infilepath, 'test'],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'mytest_fbdd41247467.test'

    # 2.2. Switch the infilepath order
    fp = generate_mock_infilepath(env=env, infilepaths=['test', infilepath],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'mytest_fbdd41247467.test'

    # 2.3. Test an example with an infilepath with a subdif
    infilepath = SourcePath(project_root='', subpath='test/mytest.html')
    fp = generate_mock_infilepath(env=env, infilepaths=[infilepath, 'test'],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'test/mytest_fbdd41247467.test'

    # 3. Test examples without extensions
    infilepath = SourcePath(project_root='test', subpath='mytest.html')
    fp = generate_mock_infilepath(env=env, infilepaths=[infilepath, 'test'])
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'mytest_fbdd41247467'

    # 4. Test examples with src_filepath
    # 4.1. Test the default src_filepath for the env. (test.dm)
    assert str(env.context['src_filepath'].subpath) == 'test.dm'
    fp = generate_mock_infilepath(env=env, infilepaths='test_text',
                                  context=env.context)
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'test_35862287bc72'

    # 4.2 Test an example with a src_filepath with a subpath
    env.context['src_filepath'] = SourcePath(project_root=env.project_root,
                                             subpath='subdir/second.dm')
    fp = generate_mock_infilepath(env=env, infilepaths='test_text',
                                  context=env.context)
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'subdir/second_35862287bc72'


def test_generate_outfilepath(env):
    """Test the genereate_outfilepath function."""

    # 1. Test with basic infilepaths
    # 1.1. Try with the cache path
    infilepath = SourcePath(project_root='test', subpath='mytest.html')
    fp = generate_outfilepath(env=env, infilepaths=infilepath, cache=True)
    assert fp.target_root == env.cache_path
    assert str(fp.subpath) == 'mytest.html'

    # 1.2. Try with the target_root (non-cached outfilepath)
    fp = generate_outfilepath(env=env, infilepaths=infilepath, cache=False)
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'mytest.html'

    # 1.3 Try with a different extension
    fp = generate_outfilepath(env=env, infilepaths=infilepath, ext='.tex')
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'mytest.tex'

