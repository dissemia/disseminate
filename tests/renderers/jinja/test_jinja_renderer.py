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


def test_jinjarenderer_is_available(doc, context_cls):
    """Test the is_available method for the JinjaRenderer."""

    # 1. Test with a document context with targets specified in the context.
    context = doc.context
    context['targets'] = ['.html', '.pdf', '.txt']
    assert context.targets == {'.html', '.pdf', '.txt'}

    # Setup a JinjaRenderer that accesses package templates only.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True)

    # An .html target should be available
    assert renderer.is_available('.html')

    # A .missing target should not be available
    assert not renderer.is_available('.missing')

    # 2. Test with a regular context with the targets specified on creation
    #    of the JinjaRenderer
    context = context_cls()

    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True, targets=['.html'])

    # An .html target should be available
    assert renderer.is_available('.html')

    # A .missing target should not be available
    assert not renderer.is_available('.missing')


def test_jinjarenderer_paths(context_cls):
    """Test the JinjaRenderer paths and template_filepaths methods."""
    # Setup the context
    src_filepath = SourcePath(project_root='tests/renderers/example1/src',
                              subpath='main.dm')
    context = context_cls(src_filepath=src_filepath,
                          targets=['.html', '.tex'])

    # 1. Setup a JinjaRenderer that accesses package templates only.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True,
                             targets=['.html', '.tex', '.txt'])

    # Check the template paths
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 4
    for s in ('disseminate/templates/default/template.html',
              'disseminate/templates/default/menu.html',
              'disseminate/templates/default/template.tex',
              'disseminate/templates/default/template.txt'):
        assert any(fp.match(s) for fp in filepaths)

    # Check the paths
    paths = renderer.paths()
    assert len(paths) == 1
    assert paths[0].match('disseminate/templates/default')

    # 2. Setup a JinjaRenderer that accesses package templates and custom
    #    templates in the project directory.
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=False,
                             targets=['.html', '.tex', '.txt'])

    # Check the template paths
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 3
    for s in ('renderers/example1/src/default/template.html',
              'disseminate/templates/default/template.tex',
              'disseminate/templates/default/template.txt'):
        assert any(fp.match(s) for fp in filepaths)

    # Check the paths
    paths = renderer.paths()
    assert len(paths) == 2
    for s in ('tests/renderers/example1/src/default',
              'disseminate/templates/default'):
        assert any(fp.match(s) for fp in paths)

    # 3. Check a template with inheritance
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True,
                             targets=['.html', '.tex'])

    # Check the template paths. The tufte book template only has '.tex' and
    # '.html' targets
    filepaths = renderer.template_filepaths()
    assert len(filepaths) == 6
    for s in ('disseminate/templates/books/tufte/template.html',
              'disseminate/templates/default/template.html',
              'disseminate/templates/default/menu.html',
              'disseminate/templates/default/nav.html',
              'disseminate/templates/books/tufte/template.tex',
              'disseminate/templates/default/template.tex'):
        assert any(fp.match(s) for fp in filepaths)


def test_jinjarenderer_context_filepaths(context_cls):
    """Test the JinjaRenderer context_filepaths method."""
    # Setup the context
    src_filepath = SourcePath(project_root='tests/renderers/example1/src',
                              subpath='main.dm')
    context = context_cls(src_filepath=src_filepath)

    # 1. Setup a JinjaRenderer that accesses package templates only.
    #    The books/tufte template has a context.txt file
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True,
                             targets=['.html', '.tex'])

    # Check the template paths
    filepaths = renderer.context_filepaths()
    assert len(filepaths) == 2
    assert filepaths[0].match('templates/books/tufte/context.txt')
    assert filepaths[1].match('templates/default/context.txt')


def test_jinjarenderer_mtime(tmpdir, context_cls, wait):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup a context
    context = context_cls(src_filepath=SourcePath())

    # 1. Try a default template
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True, targets=['.html'])
    filename = renderer.get_template(target='.html').filename

    # The renderer mtime is at least as large, or possible larger, than
    # the template file because the default template depends on multiple
    # template files through inheritance.
    assert renderer.mtime >= pathlib.Path(filename).stat().st_mtime

    # 2. Try a custom template
    project_root = SourcePath(project_root=tmpdir)
    template_root = project_root / 'default'
    template_root.mkdir()
    filename = template_root / 'template.html'
    filename.touch()

    src_filepath = SourcePath(tmpdir, 'main.dm')
    context = context_cls(src_filepath=src_filepath)
    renderer = JinjaRenderer(context=context, template='default/template',
                             module_only=False, targets=['.html'])
    t = renderer.get_template(target='.html')
    mtime = renderer.mtime
    assert mtime == filename.stat().st_mtime

    # 3. Try modifying the custom template. The mtime should be updated.
    wait() # sleep time offset needed for different mtimes
    filename.touch()
    assert renderer.mtime > mtime


def test_jinjarenderer_get_template(context_cls, tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Setup the paths
    context = context_cls(src_filepath=SourcePath(project_root=tmpdir))

    # 1. Default template
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True, targets=['.tex', '.html'])
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('disseminate/templates/default/template.html')

    # 2. Another built-in template
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True, targets=['.tex', '.html'])
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('disseminate/templates/books/tufte/template.html')

    # 3. Another built-in template (with template specified)
    renderer = JinjaRenderer(context=context, template='books/tufte/template',
                             module_only=True, targets=['.tex', '.html'])
    t = renderer.get_template(target='.html')
    filepath = pathlib.Path(t.filename)
    assert filepath.match('disseminate/templates/books/tufte/template.html')

    # 4. Try a custom template
    # Create a custom template
    template_dir = pathlib.Path(tmpdir) / 'template'
    template_dir.mkdir()
    template_file = template_dir / 'template.html'
    template_file.touch()

    renderer = JinjaRenderer(context=context, template='template',
                             targets=['.html'])
    t = renderer.get_template(target='.html')
    assert t.filename == str(template_file)


def test_jinjarenderer_add_context_paths(context_cls):
    """Test the JinjaRenderer add_context_paths method."""
    context_cls.validation_types = {'src_filepath': SourcePath}

    # 1. Default template
    src_filepath = SourcePath('')
    context = context_cls(src_filepath=src_filepath, paths=[],)
    renderer = JinjaRenderer(context=context, template='default',
                             module_only=True,
                             targets=['.html', '.tex', '.txt'])

    # Make sure the template path is correctly inserted in the context.
    # The paths are added by the constructor
    assert len(context['paths']) == 1
    assert context['paths'][0].match('disseminate/templates/default')

    # 2. Try a module template with inheritance
    context = context_cls(src_filepath=src_filepath, paths=[])
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True,
                             targets=['.html', '.tex'])

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

    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        renderer = JinjaRenderer(context=context, template='non-existent',
                                 module_only=True,
                                 targets=['.html', '.tex', '.txt'])
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
                             module_only=True,
                             targets=['.html', '.tex', '.txt'])
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
                             module_only=True,
                             targets=['.html', '.tex', '.txt'])

    renderer.render(context=context, target='.html')

    # There should be 4 dependencies now in the dep_manager: bootstrap.min.css,
    # base.css, default.css and pygments.css. These are referenced by the
    # module's default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 4
    deps = sorted(dep_manager.dependencies[src_filepath],
                  key=lambda d: d.dest_filepath)

    assert deps[0].dep_filepath.match('templates/default/media/css/base.css')
    assert deps[0].dest_filepath.match('html/media/css/base.css')
    assert deps[0].get_url() == '/html/media/css/base.css'

    assert deps[1].dep_filepath.match('templates/default/media/css/'
                                      'bootstrap.min.css')
    assert deps[1].dest_filepath.match('html/media/css/bootstrap.min.css')
    assert deps[1].get_url() == '/html/media/css/bootstrap.min.css'

    assert deps[2].dep_filepath.match('templates/default/media/css/default.css')
    assert deps[2].dest_filepath.match('html/media/css/default.css')
    assert deps[2].get_url() == '/html/media/css/default.css'

    assert deps[3].dep_filepath.match('templates/default/media/css/pygments.css')
    assert deps[3].dest_filepath.match('html/media/css/pygments.css')
    assert deps[3].get_url() == '/html/media/css/pygments.css'

    # 2. books/tufte template. The books/tufte template has a template.html that
    #    references tufte.css, which in turn references default.css
    renderer = JinjaRenderer(context=context, template='books/tufte',
                             module_only=True,
                             targets=['.html', '.tex'])
    renderer.render(context=context, target='.html')

    # There should be 4 dependencies now in the dep_manager for the .css file
    # referenced by the default/template.html file.
    assert len(dep_manager.dependencies[src_filepath]) == 4
    deps = sorted(dep_manager.dependencies[src_filepath],
                  key=lambda d: d.dest_filepath)

    # deps[0] points to base.css
    assert deps[0].dep_filepath.match('templates/default/media/css/base.css')
    assert deps[0].dest_filepath.match('html/media/css/base.css')

    # deps[1] points to bootstrap.min.css
    assert deps[1].dep_filepath.match('templates/default/media/css/'
                                      'bootstrap.min.css')
    assert deps[1].dest_filepath.match('html/media/css/bootstrap.min.css')

    # dep[2] points to tufte.css
    assert deps[2].dep_filepath.match('templates/default/media/css/'
                                      'default.css')
    assert deps[2].dest_filepath.match('html/media/css/default.css')

    # dep[3] points to pygments.css
    assert deps[3].dep_filepath.match('templates/default/media/css/'
                                      'pygments.css')
    assert deps[3].dest_filepath.match('html/media/css/pygments.css')


def test_jinjarenderer_other_targets(doc):
    """Test the JinjaRenderer shows other targets are available for a given
    template."""
    # By default, doc has 'html' as the target
    assert doc.context.targets == {'.html'}

    # doc should have 'default/template' as its default template.
    # Check that the renderer is available for other targets
    renderer = doc.context['renderers']['template']
    assert renderer.template == 'default/template'
    assert renderer.is_available('.html')

    # The other targets should be available too, as long as they're in the
    # doc.context
    assert not renderer.is_available('.tex')
    doc.context['targets'] = ['.html', '.tex']
    assert renderer.is_available('.tex')
