"""
Tests the initialize project method.
"""
import os
import glob

from disseminate.templates.init_project import (init_project, template_root,
                                                info_file)


def test_init_project(tmpdir):
    """Tests the basic functionality of init_project"""
    # Try a variety of destination paths
    for dest in (str(tmpdir), str(tmpdir) + '/'):
        # Get the files and directories in the module's project_template
        template_paths = set()
        for i in glob.iglob(os.path.join(template_root, '**'),
                            recursive=True):
            # translate to paths relative to the template_root

            rel_path = os.path.relpath(i, template_root)

            # exclude the info_file and root path
            if rel_path not in (info_file, '.'):
                # Add the rel_path to the template_paths set
                template_paths.add(rel_path)

        # Initialize a project in the tmpdir
        init_project(dest=dest, overwrite=False)

        # Get a set of directories and files created
        destination_paths = set()
        for i in glob.iglob(os.path.join(dest, '**'),
                            recursive=True):
            # Get the path relative to the destination directory
            destination_path = os.path.relpath(i, dest)

            # Skip the root
            if destination_path in ('.',):
                continue

            # add to the destination_paths
            destination_paths.add(destination_path)

        # The number and items of the destination_paths should match the
        # template_paths
        assert len(template_paths) == len(destination_paths)
        for i in destination_paths:
            assert i in template_paths

        # See if the files can be overwritten. With overwrite=False, the inodes
        # should not change
        inodes = {i: os.stat(i).st_ino
                  for i in glob.iglob(os.path.join(dest, '**'), recursive=True)
                  if os.path.isfile(i)}

        # Initialize a project in the tmpdir, disabling overwrite
        init_project(dest=dest, overwrite=False)

        # Match the inodes
        for i in glob.iglob(os.path.join(dest, '**'), recursive=True):
            if os.path.isdir(i):
                continue
            assert inodes[i] == os.stat(i).st_ino

        # Initialize a project in the tmpdir, enabling overwrite
        init_project(dest=dest, overwrite=True)

        # The inodes for the files shouldn't match now
        for i in glob.iglob(os.path.join(dest, '**'), recursive=True):
            if os.path.isdir(i):
                continue
            assert inodes[i] != os.stat(i).st_ino


