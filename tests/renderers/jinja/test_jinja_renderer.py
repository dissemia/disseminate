"""
Test the Jinja2 template renderer.
"""
import pathlib

import pytest
import jinja2
import jinja2.exceptions

from disseminate.renderers.jinja import (JinjaRenderer)
from disseminate.dependency_manager import DependencyManager
from disseminate.paths import SourcePath, TargetPath


def test_jinjarenderer_is_available(context_cls):
    """Test the is_available method for the JinjaRenderer."""

    context = context_cls()

    # 1. Setup a JinjaRenderer that accesses package templates only.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)

    # An .html target should be available
    assert renderer.is_available('.html')

    # A .missing target should not be available
    assert not renderer.is_available('.missing')


def test_jinjarenderer_paths(context_cls):
    """Test the JinjaRenderer paths and template_filepaths methods."""
    # Setup the context
    src_filepath = SourcePath(project_root='tests/renderers/example1/src',
                              subpath='main.dm')
    context = context_cls(src_filepath=src_filepath)

    # 1. Setup a JinjaRenderer that accesses package templates only.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)

    # Check the template paths
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 3
    assert filepaths[0].match('disseminate/templates/default/template.html')
    assert filepaths[1].match('disseminate/templates/default/template.tex')
    assert filepaths[2].match('disseminate/templates/default/template.txt')

    # Check the paths
    paths = renderer.paths()
    assert len(paths) == 1
    assert paths[0].match('src/disseminate/templates/default')

    # 2. Setup a JinjaRenderer that accesses package templates and custom
    #    templates in the project directory.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=False)

    # Check the template paths
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 3
    assert filepaths[0].match('renderers/example1/src/default/template.html')
    assert filepaths[1].match('disseminate/templates/default/template.tex')
    assert filepaths[2].match('disseminate/templates/default/template.txt')

    # Check the paths
    paths = renderer.paths()
    assert len(paths) == 2
    assert paths[0].match('tests/renderers/example1/src/default')
    assert paths[1].match('src/disseminate/templates/default')

    # 3. Check a template with inheritance
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True)

    # Check the template paths. The tufte book template only has '.tex' and
    # '.html' targets
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 4
    assert filepaths[0].match('disseminate/templates/books/tufte/template.html')
    assert filepaths[1].match('disseminate/templates/default/template.html')
    assert filepaths[2].match('disseminate/templates/books/tufte/template.tex')
    assert filepaths[3].match('disseminate/templates/default/template.tex')


def test_jinjarenderer_context_filepaths(context_cls):
    """Test the JinjaRenderer context_filepaths method."""
    # Setup the context
    src_filepath = SourcePath(project_root='tests/renderers/example1/src',
                              subpath='main.dm')
    context = context_cls(src_filepath=src_filepath)

    # 1. Setup a JinjaRenderer that accesses package templates only.
    #    The books/tufte template has a context.txt file
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True)

    # Check the template paths
    filepaths = renderer.context_filepaths()
    assert len(filepaths) == 1
    assert filepaths[0].match('templates/books/tufte/context.txt')


def test_jinjarenderer_mtime(tmpdir, context_cls):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup a context
    context = context_cls(src_filepath=SourcePath())

    # Default
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)
    filename = renderer.get_template(target='.html').filename
    assert renderer.mtime == pathlib.Path(filename).stat().st_mtime

    # Try a custom template
    project_root = SourcePath(project_root=tmpdir)
    template_root = project_root / 'default'
    template_root.mkdir()
    filename = template_root / 'template.html'
    filename.touch()

    src_filepath = SourcePath(tmpdir, 'main.dm')
    context = context_cls(src_filepath=src_filepath)
    renderer = JinjaRenderer(context=context, template='default/template',
                             module_only=False)
    t = renderer.get_template(target='.html')
    assert renderer.mtime == filename.stat().st_mtime


def test_jinjarenderer_get_template(context_cls, tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup the paths
    context = context_cls(src_filepath=SourcePath(project_root=tmpdir))

    # 1. Default template
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('src/disseminate/templates/default/template.html')

    # 2. Another built-in template
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True)
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('src/disseminate/templates/books/tufte/template.html')

    # 3. Another built-in template (with template specified)
    renderer = JinjaRenderer(context=context, template='books/tufte/template',
                             module_only=True)
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('src/disseminate/templates/books/tufte/template.html')

    # 4. Try a custom template
    # Create a custom template
    template_dir = pathlib.Path(tmpdir) / 'template'
    template_dir.mkdir()
    template_file = template_dir / 'template.html'
    template_file.touch()

    renderer = JinjaRenderer(context=context, template='template')
    t = renderer.get_template(target='.html')
    assert t.filename == str(template_file)


def test_jinjarenderer_add_context_paths(context_cls):
    """Test the JinjaRenderer add_context_paths method."""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)

    # Make sure the template path is correctly inserted in the context.
    # The paths are added by the constructor
    assert len(context['paths']) == 1
    assert context['paths'][0].match('disseminate/templates/default')

    # 2. Try a module template with inheritance
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True)

    # Make sure the template paths were correctly inserted in the context
    # The paths are added by the constructor
    assert len(context['paths']) == 2
    assert context['paths'][0].match('disseminate/templates/books/tufte')
    assert context['paths'][1].match('disseminate/templates/default')

    # Running it again shouldn't add more paths
    renderer.add_context_paths(context)
    assert len(context['paths']) == 2


def test_jinjarenderer_missing_template(context_cls):
    """Test the Jinja2 renderer with missing template"""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 2. Try a module template with inheritance
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='non-existent',
                             module_only=True)
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        renderer.get_template('.html')


def test_jinjarenderer_render(tmpdir, context_cls):
    """Test the JinjaRenderer render method."""
    # Setup the paths
    project_root = SourcePath()
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root)

    # Setup the root_context
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(body='', src_filepath=src_filepath,
                          project_root=project_root, target_root=target_root,
                          paths=[])

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(root_context=context)
    context['dependency_manager'] = dep_manager

    # Default template
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)
    assert '<html lang="en">' in renderer.render(context=context,
                                                 target='.html')


def test_jinjarenderer_dependencies(tmpdir, context_cls):
    """Test the Jinja2 render dependencies management."""
    tmpdir = pathlib.Path(tmpdir)

    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template. The default template has a template.html that
    #    references a default.css (media/css/default.css)
    src_filepath = SourcePath('')
    project_root = SourcePath('')
    target_root = TargetPath(target_root=tmpdir)

    # Setup the root_context
    context = context_cls(body='', src_filepath=src_filepath,
                          project_root=project_root, target_root=target_root,
                          paths=[])

    dep_manager = DependencyManager(root_context=context)
    context['dependency_manager'] = dep_manager

    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)

    renderer.render(context=context, target='.html')

    # There should be 1 dependency now in the dep_manager for the .css file
    # referenced by the default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 1
    dep = list(dep_manager.dependencies[src_filepath])[0]

    assert dep.dep_filepath.match('templates/default/media/css/default.css')
    assert dep.dest_filepath.match('html/media/css/default.css')
    assert dep.get_url() == '/html/media/css/default.css'

    # 2. books/tufte template. The books/tufte template has a template.html that
    #    references tufte.css, which in turn references default.css
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True)
    renderer.render(context=context, target='.html')

    # There should be 2 dependencies now in the dep_manager for the .css file
    # referenced by the default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 2
    dep1, dep2 = sorted(dep_manager.dependencies[src_filepath],
                        key=lambda d: d.dest_filepath)

    # dep1 points to default.css
    assert dep1.dep_filepath.match('templates/default/media/css/default.css')
    assert dep1.dest_filepath.match('html/media/css/default.css')

    # dep2 points to tufte.css
    assert dep2.dep_filepath.match('templates/books/tufte/media/css/'
                                   'tufte.css')
    assert dep2.dest_filepath.match('html/media/css/tufte.css')
