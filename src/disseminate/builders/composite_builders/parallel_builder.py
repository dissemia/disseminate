from .composite_builder import CompositeBuilder
from ...paths.utils import find_file


class ParallelBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in parallell (i.e. run the
    subbuilders together at the same time)"""

    action = 'parallel build'
    parallel = True

    def build_needed(self, reset=False):
        return any(sb.build_needed(reset=reset) for sb in self.subbuilders)

    def add_build(self, parameters, outfilepath=None, target=None,
                  context=None, in_ext=None, out_ext=None, builder_cls=None,
                  **kwargs):
        """
        Add a subbuilder to the ParallelBuilder.

        Parameters
        ----------
        parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
            The input parameters (dependencies), including filepaths, for the
            build
        outfilepath : Optional[str, :obj:`pathlib.Path`]
            The path for the output file.
        target : Optional[str]
            The document target for the build. ex: 'html' or 'tex'
        context : Optional[:obj:`.context.BaseContext`]
            The document context dict that owns the parallel builder.
        in_ext : Optional[str]
            The extension for the input file. This is used to find the correct
            builder with the find_builder_cls method. If this is not specified,
            an filepath in the parameters should be specified.
        out_ext : Optional[str]
            The extension for the input file. This is used to find the correct
            builder with the find_builder_cls method. If this is not specified,
            the outfilepath should be specified.
        builder_cls : Optional[:obj:`.builders.Builder`]
            The builder class to use in create a new build.
        **kwargs
            Optional keyword arguments to use in creating the builder.

        Returns
        -------
        builder : :obj:`.builders.Builder`
            The newly created builder.
        """
        # Setup the arguments
        context = context or self.env.context

        parameters = parameters or []
        parameters = (parameters if isinstance(parameters, list) or
                      isinstance(parameters, tuple) else [parameters])

        # Find the files in the parameters
        parameters = [find_file(i, context, raise_error=False) or i
                      for i in parameters]

        target = target or self.target

        # Find the builder class
        if builder_cls is None:
            # Get the input extensions for the builder in_ext
            if in_ext is None:
                in_exts = [infilepath for infilepath in parameters
                           if isinstance(infilepath, str) and
                           infilepath.startswith('.')]
                in_exts += [infilepath.suffix for infilepath in parameters
                            if hasattr(infilepath, 'suffix')]

                in_ext = in_exts[0] if in_exts else None

            # Get the output extension for the builder out_ext
            if out_ext is None:
                if (isinstance(outfilepath, str) and
                   outfilepath.startswith('.')):
                    out_ext = outfilepath
                elif hasattr(outfilepath, 'suffix'):
                    out_ext = outfilepath.suffix
                else:
                    out_ext = None

            builder_cls = self.find_builder_cls(in_ext=in_ext, out_ext=out_ext,
                                                target=target)

        # Create the builder
        builder = builder_cls(env=self.env, parameters=parameters,
                              outfilepath=outfilepath, context=context,
                              target=target, **kwargs)

        self.subbuilders.append(builder)

        return builder
