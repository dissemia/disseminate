from .composite_builder import CompositeBuilder


class ParallelBuilder(CompositeBuilder):
    """A composite builder that runs subbuilders in parallell (i.e. run the
    subbuilders together at the same time)"""
    parallel = True

    @property
    def status(self):
        statuses = {sb.status for sb in self.subbuilders}
        if 'inactive' in statuses:
            return 'inactive'
        elif 'missing' in statuses:
            return 'missing'
        elif 'building' in statuses:
            return 'building'
        elif {'done'} == statuses:  # all subbuilders are done
            return 'done'
        return 'ready'
