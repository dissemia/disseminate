"""
Test the target builder signals and receivers
"""


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


def test_target_builder_