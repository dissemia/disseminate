"""
Receivers for TargetBuilders
"""
from .signals import add_file


@add_file.connect_via(order=1000)
def add_file(parameters, context, in_ext, target, use_cache=False):
    """Add a file to the target builder.

    Parameters
    ----------
    parameters : Union[str, List[str, :obj:`pathlib.Path`]]
        The parameters for the build
    context : :obj:`.BaseContext`
        The document context dict
    in_ext : str
        The extension for the file.
    target : str
        The document target to add the file for.
    use_cache : Optional[bool]
        If True, use cached paths when adding files.

    Returns
    -------
    outfilepath : :obj:`pathlib.Path`
        The outfilepath for the file from the build.
    """
    # If not get the outfilepath for the given document target
    assert context.is_valid('builders')

    # Retrieve the unspecified arguments
    target = target if target.startswith('.') else '.' + target

    # Retrieve builder
    target_builder = context.get('builders', dict()).get(target)
    assert target_builder, ("A target builder for '{}' is needed in the "
                            "document context")

    build = target_builder.add_build(parameters=parameters,
                                     context=context,
                                     in_ext=in_ext,
                                     target=target,
                                     use_cache=use_cache)
    return build.outfilepath
