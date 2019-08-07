"""
View for processor listing.
"""
from inspect import isabstract

from .blueprints import system
from ..templates import render_template
from ...processors import ProcessorABC


def processors_to_dict(processor_clses, level=1):
    """Given a list of processor classes, prepare a list of dicts listing
    the sub-processors
    """
    processor_list = []

    # Sort the processor_clses
    processor_clses = [p for p in sorted(processor_clses,
                                         key=lambda p: getattr(p, 'order', -1))]
    for number, processor_cls in enumerate(processor_clses, 1):
        d = dict()

        # populate the meta data
        d['number'] = number
        d['level'] = level
        d['name'] = processor_cls.__name__
        d['isabstract'] = isabstract(processor_cls)  # is it an abstract class?

        # Get the short description, if available
        if getattr(processor_cls, 'short_desc') is not None:
            d['short_desc'] = processor_cls.short_desc

        # Get the module, if available
        if getattr(processor_cls, 'module') is not None:
            d['module'] = processor_cls.module

        # Get the order, if available
        if getattr(processor_cls, 'order') is not None:
            d['order'] = processor_cls.order

        # See if there are subclass processors to this processor class
        sub_clses = processor_cls.__subclasses__()
        if len(sub_clses) > 1:
            d['subprocessors'] = processors_to_dict(sub_clses, level=level + 1)

        processor_list.append(d)

    return processor_list


@system.route('/processors.html')
async def render_processors(request):
    """Render the view for the different types of processors available."""
    # Get the immediate subclasses for the ProcessorABC
    # These are base classes for the different processor types
    processor_subclses = ProcessorABC.__subclasses__()

    # Convert the processors to a list of dicts
    processors = processors_to_dict(processor_subclses)

    return render_template('processors.html', request=request,
                           processors=processors)
