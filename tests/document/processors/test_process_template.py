"""
Test the process_context_tempaltes processor.
"""
import pathlib

import disseminate
from disseminate import SourcePath
import disseminate.document.processors as pr


def test_template_renderer_module_templates_path(doc):
    """Test the module_templates_path method for BaseRenderer."""
    # Create a default template renderer
    context = doc.context
    context['paths'] = []
    context['src_filepath'] =SourcePath()

    # Setup the context processor
    processor = pr.process_template.ProcessContextTemplate()
    processor(context)

    renderer = context['template_renderer']

    # Get the module_templates_path. It should be in the 'templates'
    # subdirectory of the disseminate project
    disseminate_path = pathlib.Path(disseminate.__file__).parent
    templates_path = pathlib.Path(disseminate_path, 'templates').absolute()
    assert renderer.module_path == SourcePath(templates_path)

    assert context['paths'] == [templates_path / 'default']
