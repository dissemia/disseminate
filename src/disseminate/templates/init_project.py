"""
Functions to initialize a project in a directory
"""
import os.path
import shutil
import glob


# Get the current path
current_filepath = os.path.realpath(__file__)
current_path = os.path.split(current_filepath)[0]

# Get the template project path
template_root = os.path.join(current_path, 'project_template')

info_file = 'info.txt'


def init_project(dest='.', overwrite=False):
    """Initialize a project by copying directories and files from a template
    project.

    Parameters
    ----------
    dest : str, optional
        The destination directory path. If this is not specified, the current
        directory is assumed.
    overwrite : bool, optional
        If True, existing files will be overwritten.
    """
    # Print the info_file
    if dest in ('.', ''):
        dest_string = "the current directory"
    else:
        dest_string = "'" + dest + "'"

    with open(os.path.join(template_root, info_file), 'r') as f:
        print(f.read().strip().format(dest=dest_string))
    print()

    # glob through the template project
    for i in glob.iglob(os.path.join(template_root, '**'), recursive=True):
        # Get the directory and filename of the 'i' path, relative to the
        # template root
        template_path = os.path.relpath(i, template_root)

        # Skip the root directory
        if template_path in ('/', '.', ''):
            continue

        # Skip the info_file
        if template_path == info_file:
            continue

        # Create the the paths in the destination directory
        destination_path = os.path.join(dest, template_path)

        # Determine if the path is directory-like or file-like, even if it
        # doesn't exist
        is_dir = os.path.splitext(destination_path)[1] == ""

        if is_dir and not os.path.exists(destination_path):
            os.mkdir(destination_path)
            print("\tcreating directory: {}".format(destination_path))

        if not is_dir:
            if os.path.exists(destination_path):
                if overwrite:
                    os.remove(destination_path)
                    shutil.copy(os.path.join(template_root, template_path),
                                destination_path)
                    print("\toverwriting file: {}".format(destination_path))
            else:
                shutil.copy(os.path.join(template_root, template_path),
                            destination_path)
                print("\twriting file: {}".format(destination_path))

    print()
