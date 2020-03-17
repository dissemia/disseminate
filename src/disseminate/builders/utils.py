"""
Utilities for builders and environments
"""
from ..paths import SourcePath, TargetPath
from ..paths.utils import rename


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
    infilepath = [fp for fp in infilepaths if isinstance(fp, SourcePath)]
    if len(infilepaths) == 0:
        return None
    infilepath = infilepath[0]

    # Formulate the target_root
    target_root = env.cache_path if cache else env.context['target_root']

    # Formulate the target
    target = target.strip('.') if isinstance(target, str) else None

    # Formulate the subpath
    subpath = infilepath.subpath
    subpath = rename(path=subpath, append=append, extension=ext)

    # Return the new TargetPath
    return (TargetPath(target_root=target_root, target=target, subpath=subpath)
            if target else
            TargetPath(target_root=target_root, subpath=subpath))


def targetpath_to_sourcepath(targetpath):
    """Convert a TargetPath to a SourcePath"""
    return SourcePath(project_root=targetpath.target_root,
                      subpath=targetpath.subpath)
