"""
Functions to load templates for the server.

This is intentionally kept independent from the template rendering mechanism
of disseminate. That rendering mechanism is customized to work with document
contexts, which the server does not use.
"""
from sanic.exceptions import abort
from sanic.response import html
from jinja2 import Environment, PackageLoader, TemplateNotFound

#: Store the Jinja2 environment (lazy load by render_template)
jinja2_env = None


def render_template(template_name_or_list, request, **context):
    """Load the template and render with the given context dict.

    Parameters
    ----------
    template_name_or_list : Union[str, List[str]]
        The name of the template to be rendered, or an iterable with
        template names the first one existing will be rendered.
    request : :obj:`sanic.request.Request`
        The request object.
    context : dict
        The kwarg variables that should be available in the context of the
        template.
    """
    # Load the environment, if needed
    global jinja2_env
    if jinja2_env is None:
        pl = PackageLoader('disseminate', 'templates')
        jinja2_env = Environment(loader=pl)

    # Add useful functions to the context
    context['url_for'] = request.app.url_for

    try:
        template = jinja2_env.get_template(template_name_or_list)
        return html(template.render(**context))
    except TemplateNotFound:
        abort(404)
