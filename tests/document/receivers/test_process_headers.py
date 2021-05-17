"""
Test the process_header processors.
"""
from disseminate.document.receivers.process_headers import process_headers, \
    find_template_paths, find_jinja2_parent_templates, \
    find_additional_context_filepaths
from disseminate import settings


# Helper functions

def test_find_template_paths():
    """Test the find_template_paths helper function."""

    # 1. Try a default template
    paths = find_template_paths(template_name='default')
    assert len(paths) == 1
    assert paths[0] == settings.module_template_paths[0] / 'default'
    assert paths[0].is_dir()


def test_find_jinja2_parent_templates():
    """Test the find_jinja2_parent_templates helper function"""

    # 1. Load a base template (i.e. no derivation)
    template_path = settings.module_template_paths[0] / 'default'
    paths = find_jinja2_parent_templates(template_path)
    assert len(paths) == 0

    # 2. Load a derived template filepath
    template_path = settings.module_template_paths[0] / 'books' / 'tufte'
    paths = find_jinja2_parent_templates(template_path)

    assert len(paths) == 1
    assert paths[0] == settings.module_template_paths[0] / 'default'


def test_find_additional_context_filepaths():
    """Test the find_additional_context_filepaths helper function."""

    # 1. Load a base template
    paths = find_template_paths(template_name='default')
    context_paths = find_additional_context_filepaths(paths)
    assert len(context_paths) == 1
    assert (context_paths[0] ==
            settings.module_template_paths[0] / 'default' / 'context.txt')

    # 2. Load a derived template
    paths = find_template_paths(template_name='books/tufte')
    paths += find_jinja2_parent_templates(paths[0])
    context_paths = find_additional_context_filepaths(paths)
    assert len(context_paths) == 2
    assert (context_paths[0] ==
            settings.module_template_paths[0] / 'books' / 'tufte' /
            'context.txt')
    assert (context_paths[1] ==
            settings.module_template_paths[0] / 'default' / 'context.txt')


# The process_header receiver

def test_process_context_header_basic(context_cls):
    """Test the process_context_header function's basic functionality in
    loading entries from a context header entry."""

    header = """
    ---
    title: My @i{first} title
    author: Justin L Lorieau
    targets: html, tex
    macro: @i{example}
    ---
    This is my @macro body.
    """

    # Setup a context class with a targets attribute
    context = context_cls(test=header, targets='html',
                          template='default/template', paths=[])

    # Now process the context entries
    process_headers(context)

    # Ensure that the 'test' entry's header was parsed
    assert context['test'] == '    This is my @macro body.\n    '
    assert context['title'] == 'My @i{first} title'
    assert context['author'] == 'Justin L Lorieau'
    assert context['targets'] == 'html, tex'
    assert context['macro'] == '@i{example}'


def test_process_context_header_template_paths(context_cls):
    """Test the process_context_header loading of template paths."""

    # 1. Test an example with the default template
    context = context_cls(paths=[], template='default')

    process_headers(context)
    assert len(context['paths']) == 1
    assert context['paths'][0] == settings.module_template_paths[0] / 'default'

    # 2. Test an example with the books/tufte template (a derived template)
    context = context_cls(paths=[], template='books/tufte')
    process_headers(context)
    assert len(context['paths']) == 2
    assert (context['paths'][0] ==
            settings.module_template_paths[0] / 'books' / 'tufte')
    assert (context['paths'][1] ==
            settings.module_template_paths[0] / 'default')


def test_process_context_header_additional_context_files(context_cls):
    """Test the process_context_header with additional context files."""

    # 1. Try a context without loading additional context files
    context = context_cls(**settings.default_context)
    assert context['inactive_tags'] == set()

    # 1. Test an example with the default template (this one sets the
    #   'inactive_tags' entry
    context = context_cls(**settings.default_context)
    process_headers(context)
    assert context['inactive_tags'] == {'sidenote'}

    # 2. Test an example with an inherited template
    context = context_cls(**settings.default_context)
    context['template'] = 'books/tufte'
    process_headers(context)
    assert context['inactive_tags'] == {'subsubsection'}

    # 3. Test an example where a header entry in the context takes precedence
    #    over a context entry from the template
    hdr = """
    ---
    inactive_tags: some, other
    ---
    """
    context['hdr'] = hdr

    process_headers(context)
    assert context['hdr'] == '    '  # header entry processed
    assert context['inactive_tags'] == {'subsubsection', 'some', 'other'}
