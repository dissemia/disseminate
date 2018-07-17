"""
Test the Jinja2 template renderer.
"""
import os.path

from disseminate.renderers import JinjaRenderer


def test_jinja_template_search(tmpdir, context_cls):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = context_cls(targets='html', src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Another built-in template
    context = context_cls(template='books/tufte/template', targets='html',
                          src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try the same built-in template without specifying 'template' in the
    # template name.
    context = context_cls(template='books/tufte', targets='html',
                          src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = context_cls(src_filepath=str(src_filepath),
                          template='template',
                          targets='html',
                          paths=[])
    renderer = JinjaRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert t.filename == str(custom_template)
    assert '' == t.render(body='')


def test_jinja_mtime(tmpdir, context_cls):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = context_cls(targets='html', src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)
    filename = renderer.get_template(target='.html').filename
    assert renderer.mtime == os.path.getmtime(filename)

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = context_cls(src_filepath=str(src_filepath),
                          template='template',
                          targets='html',
                          paths=[])
    renderer = JinjaRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert renderer.mtime == os.path.getmtime(t.filename)


def test_jinja_template_filepaths(tmpdir, context_cls):
    """Test the template_filepaths and template_paths methods."""
    # 1. Default template
    context = context_cls(targets='html', src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)

    # Check the path relative to the module templates path and the abs path.
    # The template should have come from the module
    filenames = renderer.template_filepaths()
    correct_path = os.path.join(renderer.module_path, 'default/template.html')
    assert filenames == [correct_path]
    assert renderer.from_module

    # 2. Try a module template with inheritance
    context = context_cls(template='books/tufte',
                          targets='html',
                          src_filepath='',
                          paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)

    # The template should have come from the module
    correct_path1 = os.path.join(renderer.module_path,
                                 'books/tufte/template.html')
    correct_path2 = os.path.join(renderer.module_path,
                                 'default/template.html')

    assert renderer.template_filepaths() == [correct_path1,
                                             correct_path2]
    assert renderer.from_module

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = context_cls(src_filepath=str(src_filepath),
                          template='template',
                          targets='html',
                          paths=[])
    renderer = JinjaRenderer(context=context)

    correct_path = tmpdir.join('template.html')
    assert renderer.template_filepaths() == [str(correct_path)]
    assert not renderer.from_module


def test_jinja_context_paths(context_cls):
    """Test the template_paths method."""
    # 1. Default template
    context = context_cls(targets='html', src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)

    # Check the path relative to the module templates path and the abs path.
    # The template should have come from the module
    correct_path = os.path.join(renderer.module_path, 'default')

    # Make sure it was correctly inserted in the context
    renderer.set_context_paths(context)
    assert 'paths' in context
    assert context['paths'].count(correct_path) == 1

    # 2. Try a module template with inheritance
    context = context_cls(template='books/tufte',
                          targets='html',
                          src_filepath='',
                          paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)

    # The template should have come from the module
    correct_path1 = os.path.join(renderer.module_path,
                                 'books/tufte')
    correct_path2 = os.path.join(renderer.module_path,
                                 'default')

    # Make sure it was correctly inserted in the context
    renderer.set_context_paths(context)
    assert 'paths' in context

    # Check the paths specifically
    assert context['paths'].count(correct_path1) == 1
    assert context['paths'].count(correct_path2) == 1
    assert (context['paths'].index(correct_path1) <
            context['paths'].index(correct_path2))  # check correct ordering


def test_jinja_render(context_cls):
    """Test the Jinja2 render method."""
    # Default
    context = context_cls(body='', targets='html', src_filepath='', paths=[])
    renderer = JinjaRenderer(context=context, module_only=True)
    assert '<html lang="en">' in renderer.render(context=context,
                                                 target='.html')
