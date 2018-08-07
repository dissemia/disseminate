"""
Test the Jinja2 template renderer.
"""
import pathlib

import pytest
import jinja2.exceptions

from disseminate.renderers import JinjaRenderer, process_context_template
from disseminate.dependency_manager import DependencyManager
from disseminate.paths import SourcePath, TargetPath


def test_jinja_template_search(tmpdir, context_cls):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup the paths
    project_root = SourcePath()
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          paths=[])

    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'dependency_manager': DependencyManager}

    # Default template
    process_context_template(context)
    renderer = JinjaRenderer(context=context, targets=['.html'],
                             template='default',
                             module_only=True)
    t = renderer.get_template(target='.html')
    assert t.filename == str(pathlib.Path(renderer.module_path,
                                         'default/template.html'))
    assert '<html lang="en">' in t.render(body='')

    # Another built-in template
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, targets=['.html'],
                             template='books/tufte',
                             module_only=True)
    t = renderer.get_template(target='.html')
    assert t.filename == str(pathlib.Path(renderer.module_path,
                                          'books/tufte/template.html'))
    assert '<html lang="en">' in t.render(body='')

    # Try the same built-in template without specifying 'template' in the
    # template name.
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             targets=['.html'],
                             module_only=True)
    t = renderer.get_template(target='.html')
    assert t.filename == str(pathlib.Path(renderer.module_path,
                                          'books/tufte/template.html'))
    assert '<html lang="en">' in t.render(body='')

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = SourcePath(str(tmpdir), 'main.dm')
    context = context_cls(src_filepath=src_filepath,
                          paths=[])
    renderer = JinjaRenderer(context=context, template='template',
                             targets=['.html'])
    t = renderer.get_template(target='.html')
    assert t.filename == str(custom_template)
    assert '' == t.render(body='')


def test_jinja_mtime(tmpdir, context_cls):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup the paths
    project_root = SourcePath()
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          paths=[])

    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'dependency_manager': DependencyManager}

    # Default
    renderer = JinjaRenderer(context=context, targets=['.html'],
                             template='default', module_only=True)
    filename = renderer.get_template(target='.html').filename
    assert renderer.mtime == pathlib.Path(filename).stat().st_mtime

    # Try a custom template
    custom_template = pathlib.Path(tmpdir, 'template.html').touch()
    src_filepath = SourcePath(tmpdir, 'main.dm')
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          paths=[])
    renderer = JinjaRenderer(context=context, template='template',
                             targets=['.html'])
    t = renderer.get_template(target='.html')
    assert renderer.mtime == pathlib.Path(t.filename).stat().st_mtime


def test_jinja_template_filepaths(tmpdir, context_cls):
    """Test the template_filepaths and template_paths methods."""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='default',
                             targets=['.html'], module_only=True)

    # Check the path relative to the module templates path and the abs path.
    # The template should have come from the module
    filenames = renderer.template_filepaths()
    correct_path = pathlib.Path(renderer.module_path, 'default/template.html')
    assert filenames == [correct_path]
    assert renderer.from_module

    # 2. Try a module template with inheritance
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             targets=['.html'], module_only=True)

    # The template should have come from the module
    correct_path1 = pathlib.Path(renderer.module_path,
                                 'books/tufte/template.html')
    correct_path2 = pathlib.Path(renderer.module_path,
                                 'default/template.html')

    assert renderer.template_filepaths() == [correct_path1,
                                             correct_path2]
    assert renderer.from_module

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = SourcePath(str(tmpdir), 'main.dm')
    context = context_cls(src_filepath=src_filepath,
                          paths=[])
    renderer = JinjaRenderer(context=context, template='template',
                             targets=['.html'])

    correct_path = pathlib.Path(str(tmpdir), 'template.html')
    assert renderer.template_filepaths() == [correct_path]
    assert not renderer.from_module


def test_jinja_context_paths(context_cls):
    """Test the template_paths method."""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='default',
                             targets=['.html'], module_only=True)

    # Check the path relative to the module templates path and the abs path.
    # The template should have come from the module
    correct_path = pathlib.Path(renderer.module_path, 'default')

    # Make sure it was correctly inserted in the context
    renderer._set_context_paths(context)
    assert 'paths' in context
    assert context['paths'].count(correct_path) == 1

    # 2. Try a module template with inheritance
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             targets=['.html'], module_only=True)

    # The template should have come from the module
    correct_path1 = pathlib.Path(renderer.module_path, 'books/tufte')
    correct_path2 = pathlib.Path(renderer.module_path, 'default')

    # Make sure it was correctly inserted in the context
    renderer._set_context_paths(context)
    assert 'paths' in context

    # Check the paths specifically
    assert context['paths'].count(correct_path1) == 1
    assert context['paths'].count(correct_path2) == 1
    assert (context['paths'].index(correct_path1) <
            context['paths'].index(correct_path2))  # check correct ordering


def test_jinja_missing(context_cls):
    """Test the Jinja2 renderer with missing template"""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 2. Try a module template with inheritance
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[])
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        renderer = JinjaRenderer(context=context, template='non-existent',
                                 targets=['.html'], module_only=True)


def test_jinja_render(tmpdir, context_cls):
    """Test the Jinja2 render method."""
    # Setup the paths
    project_root = SourcePath()
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(body='',
                          dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          paths=[])

    # Default template
    renderer = JinjaRenderer(context=context, template='default',
                             targets=['.html'], module_only=True)
    assert '<html lang="en">' in renderer.render(context=context,
                                                 target='.html')


def test_jinja_render_dependencies(tmpdir, context_cls):
    """Test the Jinja2 render dependencies management."""
    tmpdir = pathlib.Path(tmpdir)

    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template. The default template has a template.html that
    #    references a default.css (media/css/default.css)
    src_filepath = SourcePath('')
    project_root = SourcePath('')
    target_root = TargetPath(target_root=tmpdir)
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    context = context_cls(body='', src_filepath=src_filepath, paths=[],
                          dependency_manager=dep_manager)
    renderer = JinjaRenderer(context=context, template='default',
                             targets=['.html'], module_only=True)

    renderer.render(context=context, target='.html')

    # There should be 1 dependency now in the dep_manager for the .css file
    # referenced by the default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 1
    dep = list(dep_manager.dependencies[src_filepath])[0]

    module_template_path = renderer.module_path
    default_template_path = pathlib.Path(module_template_path, 'default')
    tufte_template_path = pathlib.Path(module_template_path, 'books/tufte')

    assert dep.dep_filepath == SourcePath(project_root=default_template_path,
                                          subpath='media/css/default.css')
    assert dep.dest_filepath == TargetPath(target_root=target_root,
                                           target='html',
                                           subpath='media/css/default.css')
    assert dep.get_url() == '/html/media/css/default.css'

    # 2. books/tufte template. The books/tufte template has a template.html that
    #    references tufte.css, which in turn references default.css
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             targets=['.html'], module_only=True)
    renderer.render(context=context, target='.html')

    # There should be 2 dependencies now in the dep_manager for the .css file
    # referenced by the default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 2
    dep1, dep2 = sorted(dep_manager.dependencies[src_filepath],
                        key=lambda d: d.dest_filepath)

    module_template_path = renderer.module_path
    default_template_path = pathlib.Path(module_template_path, 'default')

    # dep1 points to default.css
    assert dep1.dep_filepath == SourcePath(project_root=default_template_path,
                                           subpath='media/css/default.css')
    assert dep1.dest_filepath == TargetPath(target_root=target_root,
                                            target='html',
                                            subpath='media/css/default.css')

    # dep2 points to tufte.css
    assert dep2.dep_filepath == SourcePath(project_root=tufte_template_path,
                                           subpath='media/css/tufte.css')
    assert dep2.dest_filepath == TargetPath(target_root=target_root,
                                            target='html',
                                            subpath='media/css/tufte.css')
