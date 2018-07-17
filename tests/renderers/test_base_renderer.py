"""
Tests for the base TemplateRenderer object.
"""
import os.path

import disseminate
from disseminate.renderers.base_renderer import BaseRenderer


def test_template_renderer_module_templates_path(context_cls):
    """Test the module_templates_path method for BaseRenderer."""
    # Create a default template renderer
    context = context_cls(paths=[])
    renderer = BaseRenderer(context=context)

    # Get the module_templates_path. It should be in the 'templates'
    # subdirectory of the disseminate project
    disseminate_path = os.path.split(disseminate.__file__)[0]
    templates_path = os.path.join(disseminate_path, 'templates')
    assert renderer.module_path == os.path.abspath(templates_path)

    assert context['paths'] == []
