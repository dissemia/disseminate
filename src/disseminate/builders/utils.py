"""
Utilities for builders and environments
"""
import pathlib

from .deciders.utils_hash import hash_items
from ..paths import SourcePath, TargetPath
from ..paths.utils import rename


def sort_key(parameter):
    """Sort key function for a series of parameters to give a consisting
    ordering."""
    if (isinstance(parameter, tuple) or
       isinstance(parameter, list) and parameter):
        return str(parameter[0])
    else:
        return str(parameter)


def generate_mock_parameters(env, parameters, project_root=None, subpath=None,
                             ext=None, context=None, gen_hash=True):
    """Generate a mock set of parameters.

    This function is used by builders, like JinjaRender and SaveTempFile, that
    do not use an input file but need to save to an output file. It includes
    an option to rename the filename with a hash.

    Parameters
    ----------
    env : :obj:`.builders.Environment`
        The build environment.
    parameters : Tuple[:obj:`.paths.SourcePath`, str, tuple, list]
        The parameters for the builder.
    project_root : Optional[Union[:obj:`paths.SourcePath`, str]]
        If given, use the specified project root for the mock infilepath.
    subpath : Optional[Union[:obj:`paths.SourcePath`, str]]
        If given, use the specified subpath for the mock infilepath.
    ext : Optional[str]
        If given, use the specified extension for the mock infilepath.
    gen_hash : Optional[bool]
        If True, append the hash from the given parameters to append to the
        infilepath filename.
    """
    # Setup the parameters
    parameters = parameters or []
    parameters = (parameters if isinstance(parameters, list) or
                  isinstance(parameters, tuple) else [parameters])
    subpath = pathlib.Path(subpath) if subpath is not None else None

    # First get the project root
    project_root = (project_root or env.project_root)

    # Next get the subpath
    if subpath is None:
        filepaths = [i for i in parameters if hasattr(i, 'subpath')]

        if filepaths:
            # First check to see if any of the passed parameters have a subpath
            subpath = filepaths[0].subpath.with_suffix('')
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
        # The hash is constructed from the parameters.
        hash_value = hash_items(*parameters, sort=True)[:12]  # truncate hash
    else:
        hash_value = None

    # Generate a filename with the hash
    filename = "_".join(filter(bool, [filename, hash_value]))  # Remove None
    filename = pathlib.Path(filename)

    # Set the extension, if specified
    if ext:
        filename = filename.with_suffix(ext)

    if subpath:
        return SourcePath(project_root=project_root,
                          subpath=subpath / filename)
    else:
        return SourcePath(project_root=project_root, subpath=filename)


def generate_outfilepath(env, parameters, target=None, append=None, ext=None,
                         use_cache=False, use_media=False):
    """Given a set of parameters, generate an outfilepath.

    Parameters
    ----------
    env : :obj:`.builders.Environment`
        The build environment.
    parameters : Tuple[:obj:`pathlib.Path`]
        The parameters for the builder. The first pathlib.Path will be used.
    target : Optional[str]
        If specified, use the given target as a subdirectory in the
        target_root.
    append : Optional[str]
        If specified, append the given string to the returned filename
    ext : Optional[str]
        If specified, return a cache_filepath with the given target format.
    use_cache : bool
        If True, return a path in the cache directory.
    use_media : bool
        If True, return a path with a subpath prepended with the media_path.
        ex: 'media/'

    Returns
    -------
    outfilepath : Union[:obj:`.paths.TargetPath`, None]
        The outfilepath based on the parameters given, or None if no
        outfilepath could be generated

    .. note :: When dealing with absolute paths, only the filename is kept
               in formulating the subpath. So for

               target_root = '.'
               target = 'html'
               use_media = True
               parameters = ['/usr/local/bin/2to3']

               The generated outfilepath will be:

               TargetPath('html/media/2to3')
    """
    # Find the first valid infilepath that is not an absolute path
    parameters = (parameters if isinstance(parameters, list) or
                  isinstance(parameters, tuple) else [parameters])
    parameters = [fp for fp in parameters if isinstance(fp, pathlib.Path)]

    if len(parameters) == 0:
        return None

    # Find the first infilepath that isn't an absolute path
    infilepath = parameters[0]

    # Formulate the target_root
    target_root = env.cache_path if use_cache else env.target_root
    media_path = env.media_path if use_media else None

    # Formulate the target
    if isinstance(target, str):
        target = target.strip('.')
    elif hasattr(infilepath, 'target'):
        target = infilepath.target
    else:
        target = None

    # Formulate the subpath
    subpath = (infilepath.subpath if hasattr(infilepath, 'subpath') else
               infilepath)

    # Convert the subpath to a filename, if it's an absolute path
    if hasattr(subpath, 'is_absolute') and subpath.is_absolute():
        subpath = pathlib.Path(subpath.name)

    # Add media_path, if specified
    if media_path and not str(subpath).startswith(media_path):
        subpath = rename(path=media_path / subpath, append=append,
                         extension=ext)
    else:
        subpath = rename(path=subpath, append=append, extension=ext)

    # Return the new TargetPath
    return (TargetPath(target_root=target_root, target=target, subpath=subpath)
            if target else
            TargetPath(target_root=target_root, subpath=subpath))
