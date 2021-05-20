"""
Receivers for TargetBuilders
"""
from ..builder import Builder
from ...signals import signal

add_file = signal('add_file')
find_builder = signal('find_builder')
document_tree_updated = signal('document_tree_updated')
document_build = signal('document_build')
document_build_needed = signal('document_build_needed')


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
                            "document context".format(target))

    build = target_builder.add_build(parameters=parameters,
                                     context=context,
                                     in_ext=in_ext,
                                     target=target,
                                     use_cache=use_cache)
    return build.outfilepath


# Loaded after headers but before tags are converted
@document_tree_updated.connect_via(order=2000)
def add_target_builders(root_document):
    """Add target builders to a document context"""
    # Get the subdocuments in the tree
    docs = root_document.documents_list(only_subdocuments=False,
                                        recursive=True)

    # Reset all of the builders
    for doc in docs:
        doc.context.setdefault('builders', dict()).clear()

    # Populate the target builders for each document
    for doc in docs:
        context = doc.context
        builders = context.setdefault('builders', dict())

        environment = context['environment']
        for target in context.targets:
            target = target if target.startswith('.') else '.' + target

            if target not in builders:
                builder_cls = Builder.find_builder_cls(in_ext='.dm',
                                                       out_ext=target)

                # Only add the target builder if not only_root or, if
                # only_root, the doc is equal to the root_document.
                if not builder_cls.only_root or doc == root_document:
                    builders[target] = builder_cls(env=environment,
                                                   context=context)


@find_builder.connect_via(order=1000)
def find_builder(context, target=None, **kwargs):
    """Find a target builder in a document context, or None if None was found.

    Parameters
    ----------
    context : :obj:`document.DocumentContext`
        The context dict for the document.
    target : Optional[str]
        The target to retrieve the target builder for.

    Returns
    -------
    builders : List[:obj:`.builders.target_builders.TargetBuilder`]
        Returns a list of all matching target builders.
    """
    assert 'builders' in context

    builders = context['builders']

    if target is not None:
        target = target if target.startswith('.') else '.' + target

        if target in builders:
            return [builders[target]]
        else:
            return []
    else:
        return list(builders.values())


# Loaded on document build
@document_build.connect_via(order=1000)
def build(document, complete=True):
    """Build a document tree's targets (and subdocuments) using the target
    builders."""

    # Setup a parallel builder
    context = document.context
    env = context['environment']
    root_builder = env.create_root_builder(document)

    if complete:
        while root_builder.status in {'building', 'ready'}:
            root_builder.build(complete=False)
    else:
        if root_builder.status in {'building', 'ready'}:
            root_builder.build(complete=False)

    return root_builder.status


@document_build_needed.connect_via(order=1000)
def build_needed(document):
    """Evaluate whether any of the target builders need to be build"""

    # Get the target builders
    # The builders dict should be in context from add_target_builders
    context = document.context

    assert 'builders' in context
    builders = context['builders']

    # check if any of the target builders need building
    return any(b.build_needed() for b in builders.values())
