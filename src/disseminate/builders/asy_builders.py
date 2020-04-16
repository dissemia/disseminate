"""
Builder for asymptote (.asy) files
"""
from .builder import Builder
from .save_temp import SaveTempFile
from .composite_builders import SequentialBuilder


class Asy2pdf(Builder):
    """A builder to convert from asy to pdf."""

    action = "asy -safe -f pdf -o {builder.outfilepath} {builder.infilepaths}"
    available = True
    priority = 1000
    required_execs = ('asy',)

    infilepath_ext = '.asy'
    outfilepath_ext = '.pdf'


class SaveAsyPdf(SequentialBuilder):
    """A builder that renders text to an asy file and converts it to pdf."""

    available = True
    priority = 1000
    infilepath_ext = '.save'
    outfilepath_ext = '.pdf'

    def __init__(cls, env, subbuilders=None, **kwargs):
        # setup the subbuilders
        subbuilders = subbuilders if subbuilders is not None else []

        # Setup a SaveTempFile file to save the Asy file
        save_temp = SaveTempFile(env=env, save_ext='.asy', **kwargs)
        subbuilders.append(save_temp)

        # Setup a Asy2pdf builder
        asy2pdf = Asy2pdf(env=env, **kwargs)
        subbuilders.append(asy2pdf)

        super().__init__(env=env, subbuilders=subbuilders, **kwargs)


class Asy2svg(SequentialBuilder):
    """A CompositeBuilder for Asy2svg that includes Asy2pdf and Pdf2svg
    builders.
    """

    available = True
    priority = 1000
    infilepath_ext = '.asy'
    outfilepath_ext = '.svg'

    def __init__(self, env, subbuilders=None, target=None, **kwargs):
        # Setup parameters
        subbuilders = (list(subbuilders) if isinstance(subbuilders, list) or
                       isinstance(subbuilders, tuple) else [])

        # Create the subbuilders
        asy2pdf = Asy2pdf(env=env, target=target, **kwargs)
        subbuilders.append(asy2pdf)

        pdf2svg_cls = self.find_builder_cls(in_ext='.pdf', out_ext='.svg',
                                            target=target)
        pdf2svg = pdf2svg_cls(env=env, target=target, **kwargs)
        subbuilders.append(pdf2svg)

        super().__init__(env, subbuilders=subbuilders, **kwargs)


class SaveAsySvg(SequentialBuilder):
    """A builder that renders text to an asy file and converts it to svg."""

    available = True
    priority = 1000
    infilepath_ext = '.save'
    outfilepath_ext = '.svg'

    def __init__(cls, env, subbuilders=None, **kwargs):
        # setup the subbuilders
        subbuilders = subbuilders if subbuilders is not None else []

        # Setup a SaveTempFile file to save the Asy file
        save_temp = SaveTempFile(env=env, save_ext='.asy', **kwargs)
        subbuilders.append(save_temp)

        # Setup a Asy2pdf builder
        asy2pdf = Asy2svg(env=env, **kwargs)
        subbuilders.append(asy2pdf)

        super().__init__(env=env, subbuilders=subbuilders, **kwargs)
