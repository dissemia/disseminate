"""
Utilities for builders and environments
"""
import pathlib

from ..paths import SourcePath, TargetPath
from ..paths.utils import rename
from ..utils.string import hashtxt


def generate_mock_infilepath(env, infilepaths, project_root=None, subpath=None,
                             ext=None, context=None, gen_hash=True):
    """Generate a mock infilepath.

    This function is used by builders, like JinjaRender and SaveTempFile, that
    do not use an input file but need to save to an output file. It includes
    an option to rename the filename with a hash.

    Parameters
    ----------
    env : :obj:`.builders.Environment`
        The build environment.
    infilepaths : List[:obj:`.paths.SourcePath`]
        The infilepaths for the builder.
    project_root : Optional[Union[:obj:`paths.SourcePath`, str]]
        If given, use the specified project root for the mock infilepath.
    subpath : Optional[Union[:obj:`paths.SourcePath`, str]]
        If given, use the specified subpath for the mock infilepath.
    ext : Optional[str]
        If given, use the specified extension for the mock infilepath.
    gen_hash : Optional[bool]
        If True, append the hash from the given infilepaths to append to the
        infilepath filename.
    """
    # Setup the parameters
    infilepaths = (infilepaths if isinstance(infilepaths, list)
                   or isinstance(infilepaths, tuple) else [infilepaths])
    subpath = pathlib.Path(subpath) if subpath is not None else None

    # First get the project root
    project_root = (project_root or env.project_root)

    # Next get the subpath
    if subpath is None:
        filepaths_with_subpaths = [i for i in infilepaths
                                   if hasattr(i, 'subpath')]

        if filepaths_with_subpaths:
            # First check to see if any of the passed infilepaths have a subpath
            subpath = filepaths_with_subpaths[0].subpath.with_suffix('')
        elif context is not None and 'src_filepath' in context:
            # Otherwise construct the filepath from the context's src_filepath
            src_filepath = context['src_filepath']
            subpath = src_filepath.subpath.with_suffix('')

    # Split the subpath and filename, if available and these aren't
    # specified.
    filename = getattr(subpath, 'name', None)
    subpath = getattr(subpath, 'parent', None)

    # Generate a hash
    if gen_hash:
        # The hash is constructed from the infilepaths parameters.
        hash_value = hashtxt("".join(map(hashtxt,
                                         sorted(map(str, infilepaths)))),
                             truncate=12)
    else:
        hash_value = None

    # Generate a filename with the hash
    filename = "_".join(filter(bool, [filename, hash_value]))  # Remove None
    filename = pathlib.Path(filename)

    # Set the extension, if specified
    if ext:
        filename = filename.with_suffix(ext)

    if subpath:
        return SourcePath(project_root=project_root, subpath=subpath / filename)
    else:
        return SourcePath(project_root=project_root, subpath=filename)


def generate_outfilepath(env, infilepaths, target=None, append=None, ext=None,
                         cache=False):
    """Given a set of infilepaths, generate an outfilepath.

    Parameters
    ----------
    env : :obj:`.builders.Environment`
        The build environment.
    infilepaths : List[:obj:`.paths.SourcePath`]
        The infilepaths for the builder. The first SourcePath will be used.
    target : Optional[str]
        If specified, use the given target as a subdirectory in the target_root.
    append : Optional[str]
        If specified, append the given string to the returned filename
    ext : Optional[str]
        If specified, return a cache_filepath with the given target format.
    cache : Bool
        If True, return a path in the cache directory.

    Returns
    -------
    outfilepath : Union[:obj:`.paths.TargetPath`, None]
        The outfilepath based on the parameters given, or None if no outfilepath
        could be generated
    """
    # Find the first valid infilepath
    infilepaths = (infilepaths if isinstance(infilepaths, list) or
                   isinstance(infilepaths, tuple) else [infilepaths])
    infilepaths = [fp for fp in infilepaths if hasattr(fp, 'subpath')]
    if len(infilepaths) == 0:
        return None
    infilepath = infilepaths[0]

    # Formulate the target_root
    target_root = env.cache_path if cache else env.context['target_root']

    # Formulate the target
    if isinstance(target, str):
        target = target.strip('.')
    elif hasattr(infilepath, 'target'):
        target = infilepath.target
    else:
        target = None

    # Formulate the subpath
    subpath = infilepath.subpath
    subpath = rename(path=subpath, append=append, extension=ext)

    # Return the new TargetPath
    return (TargetPath(target_root=target_root, target=target, subpath=subpath)
            if target else
            TargetPath(target_root=target_root, subpath=subpath))