"""
Test the jinja2 renderer utilities.
"""
import jinja2

from disseminate.renderers.jinja.utils import (template_paths,
                                               filepaths_from_template,
                                               filepaths_from_paths)
from disseminate import settings


def test_template_paths():
    """Test the template_paths function."""

    # Setup environments and loaders
    pl = jinja2.loaders.PackageLoader('disseminate', 'templates')
    fl = jinja2.loaders.FileSystemLoader('tests/renderers/example1/src')
    cl = jinja2.loaders.ChoiceLoader([fl, pl])

    env = jinja2.environment.Environment(loader=cl)

    # 1. Test the package loader path. It should only have 1 path for the
    #    disseminate package
    pl_path = template_paths(pl)
    assert len(pl_path) == 1
    assert pl_path[0].match('src/disseminate/templates')

    # 2. Test the filesystem loader path
    fl_path = template_paths(fl)
    assert len(fl_path) == 1
    assert fl_path[0].match('tests/renderers/example1/src')

    # 3. Test the choice loader path
    cl_paths = template_paths(cl)
    assert len(cl_paths) == 2
    assert cl_paths == fl_path + pl_path

    # 4. Test the environment (should be the same as the ChoiceLoader)
    env_paths = template_paths(env)
    assert env_paths == cl_paths


def test_jinja_filepaths_from_paths():
    """Test the filepaths_from_paths function."""

    # Setup environments and loaders
    pl = jinja2.loaders.PackageLoader('disseminate', 'templates')
    fl = jinja2.loaders.FileSystemLoader('tests/renderers/example1/src')

    # 1. Test the PackageLoader paths.
    pl_path = template_paths(pl)

    filepaths = filepaths_from_paths(pl_path, 'default')
    assert len(filepaths) == 0

    filepaths = filepaths_from_paths(pl_path, 'default/template')
    assert len(filepaths) >= 3
    assert filepaths[0].match('templates/default/template.html')
    assert filepaths[1].match('templates/default/template.tex')
    assert filepaths[2].match('templates/default/template.txt')

    # 2. Test the FileSystemLoader paths.
    fl_path = template_paths(fl)
    filepaths = filepaths_from_paths(fl_path, 'default')
    assert len(filepaths) == 0

    filepaths = filepaths_from_paths(fl_path, 'default/template')
    assert len(filepaths) == 1
    assert filepaths[0].match('example1/src/default/template.html')


def test_jinja_filepaths_from_template():
    """Test the filepaths_from_templates_function."""

    # Setup environments and loaders
    pl = jinja2.loaders.PackageLoader('disseminate', 'templates')

    kwargs = {'loader': pl,
              'block_start_string': settings.template_block_start,
              'block_end_string': settings.template_block_end}
    env = jinja2.environment.Environment(**kwargs)

    # Get a template with inherited parent templates
    template = env.get_or_select_template('books/tufte/template.html')

    # Get the paths
    paths = filepaths_from_template(template, environment=env)
    assert len(paths) > 1
    assert paths[0].match('disseminate/templates/books/tufte/template.html')
    assert paths[1].match('disseminate/templates/default/template.html')

