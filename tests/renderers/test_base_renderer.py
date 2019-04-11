"""
Tests for the base TemplateRenderer object.
"""
import pathlib

import disseminate
from disseminate.renderers.base_renderer import ProcessContextTemplate
from disseminate import SourcePath


def test_template_renderer_module_templates_path(context_cls):
    """Test the module_templates_path method for BaseRenderer."""
    # Create a default template renderer
    context = context_cls(paths=[], src_filepath=SourcePath())

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)

    renderer = context['template_renderer']

    # Get the module_templates_path. It should be in the 'templates'
    # subdirectory of the disseminate project
    disseminate_path = pathlib.Path(disseminate.__file__).parent
    templates_path = pathlib.Path(disseminate_path, 'templates').absolute()
    assert renderer.module_path == SourcePath(templates_path)

    assert context['paths'] == [templates_path / 'default']
