"""
A request handler for rendering the dependency checkers.
"""
from .server import ServerHandler
from ...checkers import Checker, All, Any, Optional


class CheckerHandler(ServerHandler):
    """A request handler for the dependency checkers"""

    def get(self):
        # Get the checkers
        checker_subclses = Checker.checker_subclasses()
        checkers = [checker_subcls() for checker_subcls in checker_subclses]

        # run the checks
        [checker.check() for checker in checkers]

        # Convert the checkers to a list of dicts
        checkers = map(self.checker_to_dict, checkers)

        self.render("checkers.html", checkers=checkers)

    def checker_to_dict(self, item, required=True, level=1):
        """Convert checkers into a list of dicts suitable for rendering the
        view."""
        d = dict()

        d['level'] = level

        # Setup the status string
        available = getattr(item, 'available', None)
        if available is True:
            d['status'] = 'ok'
        elif available is False and required:
            d['status'] = 'fail'
        elif available is False and not required:
            d['status'] = 'missing'
        else:
            d['status'] = 'unknown'

        if isinstance(item, All):
            # All are required
            msg = "Checking required dependencies for '{}'".format(
                item.category)
            d['msg'] = msg
            d['name'] = item.category
            d['subcheckers'] = [
                self.checker_to_dict(i, required=True, level=level + 1)
                for i in item]

        elif isinstance(item, Any):
            # One is required are required
            msg = "Checking alternative dependencies for '{}'".format(
                item.category)
            d['msg'] = msg
            d['name'] = item.category
            d['subcheckers'] = [
                self.checker_to_dict(i, required=False, level=level + 1)
                for i in item]

        elif isinstance(item, Optional):
            # Optional
            # One is required are required
            msg = "Checking alternative dependencies for '{}'".format(
                item.category)
            d['msg'] = msg
            d['name'] = item.category
            d['subcheckers'] = [
                self.checker_to_dict(i, required=False, level=level + 1)
                for i in item]

        elif hasattr(item, 'name'):
            msg = "Checking dependency '{}'".format(item.name)
            d['name'] = item.name
            d['msg'] = msg

        return d
