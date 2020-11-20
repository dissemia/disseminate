"""
The 'init' CLI sub-command.
"""
import pathlib
from textwrap import TextWrapper

import click

from .term import term_width
from ..utils.string import str_to_dict
from .. import settings


# Get the path for the templates directory
template_path = pathlib.Path(__file__).parent.parent / 'templates'


def filepath_key(path):
    """A sort key function for paths"""
    parts = pathlib.Path(path).parts
    num_parts = len(parts)
    return num_parts, parts



@click.command()
@click.argument('names', nargs=-1)
@click.option('--info', is_flag=True, default=False,
              help="Show detailed information on the starter")
def init(names=None, info=False):
    """Initialize a new template project"""
    if len(names) == 0:
        print_starters_list()
        exit()

    name = names[0]
    if info:
        print_starter_info(name=name)
        exit()


def starter_path_to_name(relpath):
    """Convert a starter relative path (relative to template dir) to a
    starter name"""
    parts = relpath.parts

    # Remove the 'starter' directory name and the 'description.yaml' filename
    parts = [part for part in parts
             if part != settings.template_starter_dir and
             part != settings.template_starter_desc_filename]
    return '/'.join(parts)


def starter_path_template_name(relpath):
    """Extract the template name for a given starter path"""
    parts = relpath.parts

    # Find the 'starter' directory position in the parts tuple
    pos = parts.index(settings.template_starter_dir)

    return '/'.join(parts[0:pos])


def generate_starters_dict():
    """Create a dict of available starters with the starter name as the key
    and the full path for the starter as the value."""
    # Find the configured starter directories in the template dir
    desc_filename = settings.template_starter_desc_filename
    description_filepaths = template_path.glob('**/' + desc_filename)

    starter_dict = dict()

    for path in description_filepaths:
        # Get the path relative to the template directory
        relpath = path.relative_to(template_path)

        # Generate the starter name
        name = starter_path_to_name(relpath)

        # Load the starter information
        starter = str_to_dict(path.read_text())

        # Workup the values
        starter['template'] = starter_path_template_name(relpath)
        starter['description'] = starter['description'].strip()
        starter['_relpath'] = relpath
        starter['_path'] = path

        # Generate a starter entry
        starter_dict[name] = starter

    return starter_dict


def starter_filepaths(starter):
    """Give a starter dict, return a dict with the filepaths for the files
    in the project starter.

    Parameters
    ----------
    starter : dict
        A dict with entries on the project starter. These are the entries
        (values) from the generate_starters_dict function.

    Returns
    -------
    filepaths : Dict[str, :obj:`pathlib.Path`]
        A dict with the filepaths for the project starter. The keys are
        the relative filepath strings, and the values are the full filepaths.
    """
    assert '_path' in starter
    starter_root = starter['_path'].parent

    filepaths = dict()
    for filepath in starter_root.glob('**/*'):
        if (filepath.name == settings.template_starter_desc_filename or
           not filepath.is_file()):
            continue

        relpath = filepath.relative_to(starter_root)
        filepaths[str(relpath)] = filepath

    return filepaths


def print_starters_list():
    """Print a list of available starters"""
    # Get the starter dict with the starter names
    starter_dict = generate_starters_dict()

    # Normalize the string length of starter names
    maxlength = max(len(name) for name in starter_dict.keys())

    # Setup the textwrapper
    wrap_desc = TextWrapper(subsequent_indent=' ' * (maxlength + 3),
                            width=min(80, term_width()))

    # Print the starter names and short descriptions
    for name, starter in starter_dict.items():
        # textwrap the short description
        desc = starter.get('description', '')
        line = wrap_desc.fill("{} - {}".format(name, desc))

        # Replace the name with colored text
        line = (click.style(name.ljust(maxlength), fg='cyan') +
                line[maxlength:])

        # print the starter line to terminal
        print(line)


def print_starter_info(name):
    """Print info for the starter with the given name."""
    # Get the starter dict with the starter names
    starter_dict = generate_starters_dict()

    # Make sure the starter name is listed in the starter dict
    if name not in starter_dict:
        msg = "The project starter with name '{}' could not be found."
        raise click.BadParameter(msg.format(name))

    # Retrieve the starter information
    starter = starter_dict[name]

    # Setup the textwrapper
    wrap = TextWrapper(width=min(80, term_width()),
                       initial_indent='  ', subsequent_indent='  ')

    # Print the starter name and title
    if 'title' in starter:
        print("{} ({})".format(click.style(starter['title'], bold=True),
                               click.style(name, fg='cyan')))
    else:
        print(click.style(name, fg='cyan'))

    # Print the description
    if 'description' in starter:
        desc = "\n"
        desc += click.style("Description", fg='yellow') + '\n'
        desc += wrap.fill(starter['description'])
        print(desc)

    # Print the other fields
    fields = [field for field in starter.keys()
              if field not in ('title', 'description')
              and not field.startswith('_')]
    for field in fields:
        block = "\n"
        block += click.style(field.title(), fg='yellow') + '\n'
        block += wrap.fill(starter[field])
        print(block)

    # Print a list of files in the project starter
    filepaths = starter_filepaths(starter)
    if filepaths:
        block = "\n"
        block += click.style("Files", fg='yellow') + '\n'
        for filepath in sorted(filepaths.keys(), key=filepath_key):
            block += wrap.fill(str(filepath)) + '\n'
        print(block)
