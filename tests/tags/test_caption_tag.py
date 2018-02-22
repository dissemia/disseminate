"""
Test the caption and reg tags.
"""
from disseminate.tags.caption import Caption, CaptionError
from disseminate.ast import process_ast
from disseminate.labels import LabelManager


def test_naked_caption():
    """Tests the parsing of naked captions (i.e. those not nested in a figure
    or table)."""
    # Create a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Create a mock local_context and global_context
    local_context = dict()
    global_context = {'_label_manager': label_man}

    # Generate the markup without an id
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    img = root.content[1]
    assert img.name == 'caption'
    assert img.attributes == None
    assert img.content == 'This is my caption'

    # Naked captions do not register labels
    assert len(label_man.labels) == 0


def test_figure_caption_no_id():
    """Tests the parsing of captions in figure tags when no id is specified."""
    # Create a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Create a mock local_context and global_context
    local_context = {'_src_filepath': 'src/main.dm',
                     '_targets': {'.html': 'html/main.html'}}
    global_context = {'_label_manager': label_man}

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], local_context=local_context,
                       global_context=global_context)

    fig = root.content[1]
    assert fig.name == 'marginfig'
    assert fig.attributes == None

    # Get the caption
    assert isinstance(fig.content, list)
    caption = [i for i in fig.content if isinstance(i, Caption)][0]

    assert caption.name == 'caption'
    assert caption.attributes is None
    assert caption.content == 'Fig. 1. This is my caption'

    # A label should have been registered
    assert len(label_man.labels) == 1
    label = list(label_man.labels)[0]
    assert label.id == None
    assert label.kind == 'figure'
    assert label.local_number == 1
    assert label.global_number == 1


def test_figure_caption_no_id_html():
    """Tests the html generation of captions in figure tags when no id is
    specified."""
    # Create a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Create a mock local_context and global_context
    local_context = {'_src_filepath': 'src/main.dm',
                     '_targets': {'.html': 'html/main.html'}}
    global_context = {'_label_manager': label_man}

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], local_context=local_context,
                       global_context=global_context)

    # Test the caption's html
    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    root_html = root.html()
    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    assert root_html == ('<span class="marginfig">'
                         '<span class="caption">'
                         'Fig. 1. This is my caption'
                         '</span>'
                         '</span>')


def test_figure_caption_no_id_tex():
    """Tests the tex generation of captions in figure tags when no id is
    specified."""
    # Create a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Create a mock local_context and global_context
    local_context = {'_src_filepath': 'src/main.dm',
                     '_targets': {'.html': 'html/main.html'}}
    global_context = {'_label_manager': label_man}

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], local_context=local_context,
                       global_context=global_context)

    root_tex = root.tex()
    assert root_tex == ('\n\\begin{marginfigure}\n'
                        '\\caption{Fig. 1. This is my caption}\n'
                        '\\end{marginfigure}\n')


def test_figure_caption_with_id():
    """Tests the parsing of captions in figure tags when an id is specified."""
    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    for src in ("@marginfig[id=fig-1]{@caption{This is my caption}}",
                "@marginfig{@caption[id=fig-1]{This is my caption}}"):

        # Create a label manager
        label_man = LabelManager(project_root='src', target_root='.',
                                 segregate_targets=True)

        # Create a mock local_context and global_context
        local_context = {'_src_filepath': 'src/main.dm',
                         '_targets': {'.html': 'html/main.html'}}
        global_context = {'_label_manager': label_man}

        # Generate a tag and compare the generated tex to the answer key
        root = process_ast([src], local_context=local_context,
                           global_context=global_context)

        fig = root.content[1]
        assert fig.name == 'marginfig'

        # Get the caption
        assert isinstance(fig.content, list)
        caption = [i for i in fig.content if isinstance(i, Caption)][0]

        assert caption.name == 'caption'
        assert caption.content == 'Fig. 1. This is my caption'

        # A label should have been registered
        assert len(label_man.labels) == 1
        label = list(label_man.labels)[0]
        assert label.id == 'fig-1'
        assert label.kind == 'figure'
        assert label.local_number == 1
        assert label.global_number == 1


def test_figure_caption_with_id_html():
    """Tests the html generation of captions in figure tags when an id is
    specified."""
    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Create a label manager
        label_man = LabelManager(project_root='src', target_root='.',
                                 segregate_targets=True)

        # Create a mock local_context and global_context
        local_context = {'_src_filepath': 'src/main.dm',
                         '_targets': {'.html': 'html/main.html'}}
        global_context = {'_label_manager': label_man}

        # Generate a tag and compare the generated tex to the answer key
        root = process_ast([src], local_context=local_context,
                           global_context=global_context)

        # Test the caption's html
        # The following root tags have to be stripped for the html strings
        root_start = '<span class="root">'
        root_end = '</span>\n'

        root_html = root.html()
        # Remove the root tag
        root_html = root_html[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

        if count == 0:
            assert root_html == ('<span id="fig-1" class="marginfig">'
                                 '<span class="caption">'
                                 'Fig. 1. This is my caption'
                                 '</span>'
                                 '</span>')
        elif count == 1:
            assert root_html == ('<span class="marginfig">'
                                 '<span id="fig-1" class="caption">'
                                 'Fig. 1. This is my caption'
                                 '</span>'
                                 '</span>')


def test_figure_caption_with_id_tex():
    """Tests the tex generation of captions in figure tags when an id is
    specified."""
    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Create a label manager
        label_man = LabelManager(project_root='src', target_root='.',
                                 segregate_targets=True)

        # Create a mock local_context and global_context
        local_context = {'_src_filepath': 'src/main.dm',
                         '_targets': {'.html': 'html/main.html'}}
        global_context = {'_label_manager': label_man}

        # Generate a tag and compare the generated tex to the answer key
        root = process_ast([src], local_context=local_context,
                           global_context=global_context)

        root_tex = root.tex()
        assert root_tex == ('\n\\begin{marginfigure}\n'
                            '\\caption{Fig. 1. This is my caption}\n'
                            '\\end{marginfigure}\n')

