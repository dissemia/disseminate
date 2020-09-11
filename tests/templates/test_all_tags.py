"""
Tests for all templates
"""
import pathlib
from os import curdir

from disseminate import __path__ as path
from disseminate import settings
from disseminate.tags import TagFactory


def test_all_tags_and_templates_tex(doc):
    """Test the use of all tags with all templates."""
    # Get a list of all tags
    tag_classes = TagFactory.tag_classes()

    # Get the path for the built-in templates
    template_basepath = pathlib.Path(path[0]) / 'templates'

    # find the templates
    target = '.tex'
    template_paths = template_basepath.glob('**/template' + target)
    templates = [p.relative_to(template_basepath) for p in template_paths]
    templates = [str(p).replace(target, '')
                 for p in templates]

    # Try processing the documents with all the tags
    for template in sorted(templates):
        src = ("---\n"
               "template: {}\n"
               "target: pdf\n"
               "title: My Title\n"
               "---\n").format(template)

        for tag in sorted(tag_classes.keys()):

            # Prepare the attributes. Some tags have special attribute
            # requirements
            if tag == 'panel':
                attrs = '[width=100%]'
            else:
                attrs = ''

            # Add the tag to the source body. Some tags have special content
            tag_src = settings.tag_prefix + tag + attrs + '{'
            if tag == 'asy':
                img_path = (pathlib.Path(curdir).absolute() / 'tests' /
                            'builders' / 'examples' / 'ex7' / 'diagram.asy')
                tag_src += str(img_path)
            elif tag == 'caption':
                tag_src = (settings.tag_prefix + "@figure{" +
                           settings.tag_prefix + "@caption{caption}")
            elif tag == 'img':
                img_path = (pathlib.Path(curdir).absolute() /
                            'tests' / 'templates' / 'examples' /
                            'ex1' / 'sample.png')
                tag_src += str(img_path)
            elif tag == 'list':
                tag_src += "- my list"
            elif tag == 'ref':
                tag_src += 'doc:' + doc.doc_id.replace('.', '-')
            elif tag == 'smb' or tag == 'symbol':
                tag_src += 'alpha'
            elif tag == 'supsub':
                tag_src += 'one && two'
            else:
                tag_src += tag
            tag_src += '}\n'
            src += tag_src

        # Write the source document
        doc.src_filepath.write_text(src)
        doc.load()
        doc.build()
