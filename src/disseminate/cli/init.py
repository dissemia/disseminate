"""
The 'init' CLI sub-command.
"""
import pathlib
from textwrap import TextWrapper, dedent
from shutil import copy2

import click

from .term import term_width, wrap_with_newlines
from ..utils.string import str_to_dict
from .. import settings


# Get the path for the templates directory
template_path = pathlib.Path(__file__).parent.parent / 'templates'


@click.command()
@click.argument('names', nargs=-1)
@click.option('--out-dir', '-o', required=False,
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default=None,
              help="the directory to create the project starter")
@click.option('--info', is_flag=True, default=False,
              help="Show detailed information on the specified project "
                   "starter")
@click.option('-l', '--list', 'show_list',
              is_flag=True, default=False,
              help="List the available project starters")
def init(names=None, out_dir=None, info=False, show_list=False):
    """Initialize a new template project"""
    starters_dict = generate_starters_dict()

    if len(names) == 0 or show_list:
        print_starters_list(starters_dict)
        exit()

    name = names[0]

    # Make sure the starter name is listed in the starter dict
    if name not in starters_dict:
        msg = "The project starter with name '{}' could not be found."
        raise click.BadParameter(msg.format(name))

    # Retrieve the starter
    starter = starters_dict[name]

    # Print the detailed info, if specified
    if info:
        print_starter_info(name=name, starter=starter)
        exit()

    # At this stage, try cloning the project starter
    clone_starter(name=name, starter=starter, out_dir=out_dir)


def filepath_key(path):
    """A sort key function for paths"""
    parts = pathlib.Path(path).parts
    num_parts = len(parts)
    return num_parts, parts


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

    # Find the 'starters' directory position in the parts tuple
    pos = parts.index(settings.template_starter_dir)

    return '/'.join(parts[0:pos])


def generate_starters_dict():
    """Create a dict of available starters with the starter name as the key
    and the full path for the starter as the value.

    Returns
    -------
    starters_dict : Dict[str, Dict[str,str]]
        A dict for all available project starters. The key is the starter name
        (str) and the value is a starter dict with the description of the
        starter.
    """
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


def print_starters_list(starters_dict):
    """Print a list of available starters

    Parameters
    ----------
    starters_dict : Dict[str, Dict[str,str]]
        A dict for all available project starters. The key is the starter name
        (str) and the value is a starter dict with the description of the
        starter.
    """
    twidth = min(80, term_width())
    name_clr = settings.cli_init_starter_name_color

    # Normalize the string length of starter names
    max_len = max(len(name) for name in starters_dict.keys())

    # Setup the textwrapper
    wrap = TextWrapper(subsequent_indent=' ' * (max_len + 3),
                       width=twidth)

    # Print the starter names and short descriptions
    for name in sorted(starters_dict):
        starter = starters_dict[name]

        # textwrap the short description
        name_len = len(name)
        start = click.style(name, fg=name_clr)
        start += " " * (max_len - name_len)  # left justify

        desc = starter.get('description', '')
        desc = desc.splitlines()[0]  # keep only the first line
        end = wrap.fill(desc)

        # Replace the name with colored text
        line = " - ".join((start, end))

        # print the starter line to terminal
        print(line)


def print_starter_info(name, starter):
    """Print info for the starter with the given name.

    Parameters
    ----------
    name : str
        The project starter name.
    starter : dict
        A dict with entries on the project starter. These are the entries
        (values) from the generate_starters_dict function.
    """
    # Setup the textwrapper and cli settings
    name_clr = settings.cli_init_starter_name_color
    heading_clr = settings.cli_init_starter_subheadind_color

    wrap = TextWrapper(width=min(80, term_width()),
                       initial_indent='  ', subsequent_indent='  ')

    # Print the starter name and title
    if 'title' in starter:
        print("{} ({})".format(click.style(starter['title'], bold=True),
                               click.style(name, fg=name_clr)))
    else:
        print(click.style(name, fg=name_clr))

    # Print the description
    if 'description' in starter:
        description = dedent("  " + starter['description'])

        block = "\n"
        block += click.style("Description", fg=heading_clr) + '\n'
        block += wrap_with_newlines(description, wrapper=wrap)
        print(block)

    # Print the other fields
    fields = [field for field in starter.keys()
              if field not in ('title', 'description') and not
              field.startswith('_')]
    for field in fields:
        block = "\n"
        block += click.style(field.title(), fg=heading_clr) + '\n'
        block += wrap_with_newlines(starter[field], wrapper=wrap)
        print(block)

    # Print a list of files in the project starter
    filepaths = starter_filepaths(starter)
    if filepaths:
        block = "\n"
        block += click.style("Files", fg=heading_clr) + '\n'
        for filepath in sorted(filepaths.keys(), key=filepath_key):
            block += wrap.fill(str(filepath)) + '\n'
        print(block)


def is_empty(path):
    """Returns True if the path is a directory and it's empty."""
    path = pathlib.Path(path)
    if not path.is_dir():
        return False
    try:
        next(path.iterdir())
    except StopIteration:
        return True

    return False


def clone_starter(name, starter, out_dir):
    """Clone the given project starter to the out_dir.

    Parameters
    ----------
    name : str
        The project starter name.
    starter : dict
        A dict with entries on the project starter. These are the entries
        (values) from the generate_starters_dict function.
    out_dir : str
        The directory to create the starter template copy.
    """
    twidth = min(80, term_width())
    name_clr = settings.cli_init_starter_name_color

    out_dir = (pathlib.Path(out_dir) if out_dir is not None else
               pathlib.Path('.'))

    wrap = TextWrapper(width=twidth)

    # Check to see if the destination directory is empty
    msg = ("The directory '{}' is not empty; do you still want to initialize "
           "the project?")
    msg = wrap.fill(msg.format(out_dir))
    if not is_empty(out_dir) and not click.confirm(msg):
        exit()

    # Ok, we're good to clone the project starter
    filepaths = starter_filepaths(starter)
    max_filepath_len = max(len(filepath) for filepath in filepaths)

    for filepath in sorted(filepaths, key=filepath_key):
        full_filepath = filepaths[filepath]

        # Format the printed message
        src = filepath
        dest = out_dir / filepath

        start = "Copying {}{}".format(name + '/', src)
        start += " " * (max_filepath_len - len(str(src)) + 1)
        end = "-> {}".format(dest)

        # Colorize the text
        len_str = len(start + end)
        start = "Copying {}{}".format(click.style(name + '/', fg=name_clr),
                                      src)
        start += " " * (max_filepath_len - len(str(src)) + 1)

        if len_str > twidth:
            print("\n  ".join((start, end)))
        else:
            print("".join((start, end)))

        # Make the destination directory
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(full_filepath, dest)
