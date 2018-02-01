"""
Test the template classes and functions.
"""
import disseminate
from disseminate.templates import get_template


def test_load_module_template():
    """Tests the proper loading of templates in the module."""

    # Get the default template
    t = get_template('', target='.html')

    # Got the module path
    path = disseminate.__path__[0]

    # Make sure the template exists and that it's in the module package
    assert t is not None
    assert path in t.filename


def test_local_template():
    """Tests the loading of a local template file (i.e. a template in the same
    directory as the source file.)"""

    # Example1 has an index.dm and template.html file
    path = 'tests/templates/examples1'
    dm_file = path + '/index.dm'

    # Get the template
    t = get_template(dm_file, target='.html')

    # Make sure the template exists and that it's in the module package
    assert t is not None
    assert path in t.filename
