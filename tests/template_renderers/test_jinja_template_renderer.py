"""
Test the Jinja2 template renderer.
"""
import os.path

from disseminate.template_renderers import JinjaTemplateRenderer


def test_jinja_template_search(tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = {'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Another built-in template
    context = {'template': 'books/tufte/template',
               'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try the same built-in template without specifying 'template' in the
    # template name.
    context = {'template': 'books/tufte',
               'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context, module_only=True)
    t = renderer.get_template(target='.html')
    assert '<html lang="en">' in t.render(body='')

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = {'src_filepath': str(src_filepath),
               'template': 'template',
               'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert t.filename == str(custom_template)
    assert '' == t.render(body='')


def test_jinja_mtime(tmpdir):
    """Test the correct loading of paths by the Jinja2 template renderer."""
    # Default
    context = {'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context, module_only=True)
    filename = renderer.get_template(target='.html').filename
    assert renderer.mtime == os.path.getmtime(filename)

    # Try a custom template
    custom_template = tmpdir.join('template.html').ensure(file=True)
    src_filepath = tmpdir.join('main.dm')
    context = {'src_filepath': str(src_filepath),
               'template': 'template',
               'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context)
    t = renderer.get_template(target='.html')
    assert renderer.mtime == os.path.getmtime(t.filename)


def test_jinja_render():
    """Test the Jinja2 render method."""
    # Default
    context = {'body': '',
               'targets': 'html'}
    renderer = JinjaTemplateRenderer(context=context, module_only=True)
    assert '<html lang="en">' in renderer.render(context=context,
                                                 target='.html')
