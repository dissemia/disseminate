"""
Test the target builder receivers.
"""
from disseminate.signals import signal
from disseminate.builders.target_builders import HtmlBuilder
from disseminate.paths import TargetPath

add_dependencies = signal('add_dependencies')


def test_html_builder_add_dependencies(env):
    """Test target builders (HtmlBuilder) with the add_dependencies signal"""
    context = env.context
    src_filepath = context['src_filepath']

    # 1. Setup the builder without an outfilepath.
    builder = HtmlBuilder(env, context=context)

    assert builder.parameters == ["build 'HtmlBuilder'", src_filepath]
    assert builder.build_needed()
    assert builder.build(complete=True) == 'done'
    assert not builder.build_needed()

    # 2. Now try adding a dependency. This will add a parameter to the target
    #    builder, which will require a new build
    receivers = add_dependencies.receivers.copy()

    try:
        @add_dependencies.connect_via(order=2000)
        def add_param(context):
            return ['extra']

        assert builder.parameters == ["build 'HtmlBuilder'", src_filepath, 'extra']
        assert builder.build_needed()
        assert builder.build(complete=True) == 'done'
        assert not builder.build_needed()
    except AssertionError as e:
        raise e
    finally:
        add_dependencies.receivers = receivers

