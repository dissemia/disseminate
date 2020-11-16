"""
Test utils for builders
"""
import pathlib
import os.path

from disseminate.builders.utils import (sort_key, generate_mock_parameters,
                                        generate_outfilepath)
from disseminate.paths import SourcePath


ex6_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex6'


def test_sort_key():
    """Test the sort_key for parameters"""
    assert (sorted(['test', 'abc', 123], key=sort_key) ==
            [123, 'abc', 'test'])
    assert (sorted(['test', ('scale', 2.0), 123], key=sort_key) ==
            [123, ('scale', 2.0), 'test'])


def test_generate_mock_infilepath(env):
    """Test the generate_mock_parameters function."""

    # 1. Test examples with simple strings
    fp = generate_mock_parameters(env=env, parameters='test_text', ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'fc08987284ae.test'

    # 2. Test examples with other source files
    # 2.1. Test an example with an infilepath in the parameters
    infilepath = SourcePath(project_root=ex6_root, subpath='index.dm')
    fp = generate_mock_parameters(env=env, parameters=[infilepath, 'test'],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'index_bccea4e70d82.test'

    # 2.2. Switch the infilepath order and the hash should be the same
    fp = generate_mock_parameters(env=env, parameters=['test', infilepath],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'index_bccea4e70d82.test'

    # 2.3. Test an example with an infilepath with a subdir
    infilepath = SourcePath(project_root=ex6_root, subpath='sub1/index.dm')
    fp = generate_mock_parameters(env=env, parameters=[infilepath, 'test'],
                                  ext='.test')
    assert fp.project_root == env.project_root
    assert fp.subpath == pathlib.Path('sub1') / 'index_39b849c89733.test'

    # 3. Test examples without extensions
    fp = generate_mock_parameters(env=env, parameters=[infilepath, 'test'])
    assert fp.project_root == env.project_root
    assert fp.subpath == pathlib.Path('sub1') / 'index_39b849c89733'

    # 4. Test examples with src_filepath
    # 4.1. Test the default src_filepath for the env. (test.dm)
    assert str(env.context['src_filepath'].subpath) == 'test.dm'
    fp = generate_mock_parameters(env=env, parameters='test_text',
                                  context=env.context)
    assert fp.project_root == env.project_root
    assert str(fp.subpath) == 'test_fc08987284ae'

    # 4.2 Test an example with a src_filepath with a subpath
    env.context['src_filepath'] = SourcePath(project_root=env.project_root,
                                             subpath='subdir/second.dm')
    fp = generate_mock_parameters(env=env, parameters='test_text',
                                  context=env.context)
    assert fp.project_root == env.project_root
    assert fp.subpath == pathlib.Path('subdir') / 'second_fc08987284ae'


def test_generate_outfilepath(env):
    """Test the genereate_outfilepath function."""

    # 1. Test with basic parameters and a cache path
    infilepath = SourcePath(project_root='test', subpath='mytest.html')
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=True,
                              use_media=False)
    assert fp.target_root == env.cache_path
    assert str(fp.subpath) == 'mytest.html'

    # 2. Test with basic parameters and  with the target_root
    #    (non-cached outfilepath)
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=False)
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'mytest.html'

    # 3. Test with basic parameters and try with a different extension
    fp = generate_outfilepath(env=env, parameters=infilepath, ext='.tex')
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'mytest.tex'

    # 5. Test with base parameters and a cache and media path
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=True,
                              use_media=True)
    assert fp.target_root == env.cache_path
    assert str(fp.subpath) == 'media/mytest.html'

    # 6. Test with base parameters and a media path
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=False,
                              use_media=True)
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'media/mytest.html'

    # 7. Try removing the media_path from the context. A media_path will not
    #    be prepended to the subpath
    del env.context['media_path']
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=False,
                              use_media=True)
    assert fp.target_root == env.target_root
    assert str(fp.subpath) == 'mytest.html'

    # 8. Try an example with a pathlib.Path object
    infilepath = pathlib.Path('test') / 'mytest.html'
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=True,
                              use_media=False)
    assert fp == env.cache_path / 'test' / 'mytest.html'

    # 9. Try an example with a pathlib.Path object and a use_media path
    env.context['media_path'] = 'media'
    fp = generate_outfilepath(env=env, parameters=infilepath, use_cache=False,
                              use_media=True)
    assert fp == env.target_root / 'media' / 'test' / 'mytest.html'

    # 10. Test an example with an absolute path (pathlib.Path object)
    curdir = pathlib.Path(os.path.curdir).resolve()
    infilepath = curdir / 'test' / 'mytest.html'
    fp = generate_outfilepath(env=env, parameters=[infilepath],
                              use_cache=False, use_media=True)
    assert fp == env.target_root / 'media' / 'mytest.html'

    # 11. Test an example with an absolute path (SourcePath object)
    infilepath = SourcePath(project_root=curdir,
                            subpath='test/mytest.html')
    fp = generate_outfilepath(env=env, parameters=[infilepath],
                              use_cache=False, use_media=True)
    assert fp == env.target_root / 'media' / 'test' / 'mytest.html'

    # 12. Test an example with an absolute path with a non-existent file (str)
    infilepath = SourcePath(project_root=curdir,
                            subpath='test/mytest.html')
    fp = generate_outfilepath(env=env, parameters=[str(infilepath)],
                              use_cache=False, use_media=True)
    assert fp is None

    # 13. Test an example with an absolute path with an existing file (str)
    infilepath = SourcePath(project_root=curdir,
                            subpath='tests/builders/examples/ex9/1.pdf')
    fp = generate_outfilepath(env=env, parameters=[str(infilepath)],
                              use_cache=False, use_media=True)
    assert fp is None
