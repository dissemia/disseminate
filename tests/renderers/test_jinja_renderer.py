"""
Test the Jinja2 template renderer.
"""
import os.path

from disseminate.renderers import JinjaRenderer


def test_jinja_template_search(tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = {'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Another built-in template
    context = {'template': 'books/tufte/template',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try the same built-in template without specifying 'template' in the
    # template name.
    context = {'template': 'books/tufte',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = {'src_filepath': str(src_filepath),
               'template': 'template',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert t.filename == str(custom_template)
    assert '' == t.render(body='')


def test_jinja_mtime(tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = {'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)
    filename = renderer.get_template(target='.html').filename
    assert renderer.mtime == os.path.getmtime(filename)

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = {'src_filepath': str(src_filepath),
               'template': 'template',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert renderer.mtime == os.path.getmtime(t.filename)


def test_jinja_template_filepaths(tmpdir):
    """Test the template_filepaths and template_paths methods."""
    # 1. Default template
    context = {'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)

    # Check the path relative to the module templates path and the abs path.
    # The template should have come from the module
    filenames = renderer.template_filepaths()
    correct_path = os.path.join(renderer.module_path, 'default/template.html')
    assert filenames == [correct_path]
    assert renderer.from_module

    # Check the template_paths method
    template_path = os.path.join(renderer.module_path, 'default')
    assert renderer.template_paths() == [template_path]

    # 2. Try a module template with inheritance
    context = {'template': 'books/tufte',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)

    # The template should have come from the module
    correct_path1 = os.path.join(renderer.module_path,
                                 'books/tufte/template.html')
    correct_path2 = os.path.join(renderer.module_path,
                                 'default/template.html')

    assert renderer.template_filepaths() == [correct_path1,
                                             correct_path2]
    assert renderer.from_module

    # Check the template_paths method
    template_path1 = os.path.join(renderer.module_path, 'books/tufte')
    template_path2 = os.path.join(renderer.module_path, 'default')
    assert renderer.template_paths() == [template_path1, template_path2]

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = {'src_filepath': str(src_filepath),
               'template': 'template',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context)

    correct_path = tmpdir.join('template.html')
    assert renderer.template_filepaths() == [str(correct_path)]
    assert not renderer.from_module

    # Check the template_paths method
    template_path = str(tmpdir)
    assert renderer.template_paths() == [template_path]


def test_jinja_render():
    """Test the Jinja2 render method."""
    # Default
    context = {'body': '',
               'targets': 'html'}
    renderer = JinjaRenderer(context=context, module_only=True)
    assert '<html lang="en">' in renderer.render(context=context,
                                                 target='.html')
