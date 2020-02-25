"""
Utilities for builders and environments
"""
from ..paths import SourcePath, TargetPath


def cache_filepath(path, env, append=None, ext=None):
    """Generate a filepath in a cache directory.

    Parameters
    ----------
    path : Union[:obj:`.paths.SourcePath`, :obj:`.paths.TargetPath`]
        The path to convert to a cache path.
    env : :obj:`.builders.Environment`
        The build environment.
    append : Optional[str]
        If specified, append the given string to the returned filename
    ext : Optional[str]
        If specified, return a cache_filepath with the given target format.

    Returns
    -------
    cache_filepath : :obj:`.paths.SourcePath`
        The filepath for the file in the cache directory.
    """
    # Get the path for the cache directory
    cache_path = env.cache_path

    # Format the subpath
    subpath = path.subpath

    if isinstance(append, str):
        subpath = subpath.with_name(subpath.stem + append + subpath.suffix)

    if isinstance(ext, str):
        ext = ext if ext.startswith('.') else '.' + ext
        subpath = subpath.with_suffix(ext)

    return TargetPath(target_root=cache_path, subpath=subpath)


def targetpath_to_sourcepath(targetpath):
    """Convert a TargetPath to a SourcePath"""
    return SourcePath(project_root=targetpath.target_root,
                      subpath=targetpath.subpath)
