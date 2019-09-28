"""
Tests for all templates
"""
import pathlib
from os import curdir

from disseminate import __path__ as path
from disseminate import settings
from disseminate.tags import TagFactory, Tag


def test_all_tags_and_templates_tex(doc):
    """Test the use of all tags with all templates."""
    # Get a list of all tags
    factory = TagFactory(tag_base_cls=Tag)
    tag_classes = factory.tag_classes

    # Get the path for the built-in templates
    template_basepath = pathlib.Path(path[0]) / 'templates'

    # find the templates
    target = '.tex'
    template_paths = template_basepath.glob('**/template' + target)
    templates = [p.relative_to(template_basepath) for p in template_paths]
    templates = [str(p).replace(target, '')
                 for p in templates]

    # Try processing the documents with all the tags
    for template in templates:
        src = ("---\n"
               "template: {}\n"
               "target: pdf\n"
               "---\n").format(template)

        for tag in list(tag_classes.keys())[:24]:
            # Prepare the attributes. Some tags have special attribute
            # requirements
            if tag == 'panel':
                attrs = '[100%]'
            else:
                attrs = ''

            # Add the tag to the source body. Some tags have special content
            src += settings.tag_prefix + tag + attrs + '{'
            if tag == 'supsub':
                src += 'one && two'
            elif tag == 'img':
                img_path = (pathlib.Path(curdir).absolute() /
                            'tests' / 'templates' / 'example1' / 'sample.png')
                src += str(img_path)
            elif tag == 'ref':
                src += 'doc:' + doc.doc_id.replace('.', '-')
            elif tag == 'smb' or tag == 'symbol':
                src += 'alpha'
            else:
                src += tag
            src += '}\n'
        print(src.splitlines()[-1])
        # Write the source document
        doc.src_filepath.write_text(src)
        doc.load()
        doc.render()

