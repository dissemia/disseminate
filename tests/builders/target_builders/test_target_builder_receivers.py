"""
Test the target builder signals and receivers
"""
from disseminate.signals.signals import signal

find_builder = signal('find_builder')


def test_add_target_builders(env):
    """Test the add_targets_builders receiver with reloading of document
    targets"""

    # 1. Create a document with one target
    doc = env.root_document
    doc.src_filepath.write_text("""
    ---
    targets: html
    ---
    """)
    doc.load()
    assert doc.context['builders'].keys() == {'.html'}

    # 2. Create a document with two targets
    doc = env.root_document
    doc.src_filepath.write_text("""
        ---
        targets: html, tex
        ---
        """)
    doc.load()
    assert doc.context['builders'].keys() == {'.html', '.tex'}


def test_find_builder(env):
    """Test the find_builder receiver."""

    # 1. Get the document targets
    target_root = env.target_root
    context = env.root_document.context
    targets = context.targets
    assert targets == {'.html', '.pdf', '.tex', '.xhtml'}

    for target in targets:
        builders = find_builder.emit(context=context, target=target)
        assert len(builders) == 1

    # Find all target builders. The signal wraps th results in a list.
    # The first item should contain all 3 target builders
    target_builders = find_builder.emit(context=context)
    assert len(target_builders) == 1
    assert len(target_builders[0]) == 4
