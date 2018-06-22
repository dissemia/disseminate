"""
Test the header functions.
"""
from disseminate.header import parse_header_str, load_header
from disseminate.utils.string import str_to_list
from disseminate import settings


def test_parse_header_str():
    """Tests the parsing of header strings."""

    # Test simple 1-liners
    assert parse_header_str("""entry: one""") == {'entry': 'one'}
    assert parse_header_str("""entry: 1""") == {'entry': '1'}

    # Test simple multiple entries
    assert (parse_header_str("entry: one\ntest:two")
                            == {'entry': 'one', 'test': 'two'})
    assert (parse_header_str("entry: one\n@macro:two") ==
            {'entry': 'one', '@macro': 'two'})

    # Test macro entries
    assert (parse_header_str('@feature: @div[class="col-md-4" id=4]') ==
            {'@feature': '@div[class="col-md-4" id=4]'})

    # Entries with tags
    assert (parse_header_str("toc: @toc{all documents}") ==
            {'toc': '@toc{all documents}'})
    assert (parse_header_str("toc: @toc{all \n"
                             "documents}") ==
            {'toc': '@toc{all \ndocuments}'})
    assert (parse_header_str("""toc: @toc{all
                             documents}""") ==
            {'toc': '@toc{all\n                             documents}'})

    # Nested entries
    header = """
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    """
    d = parse_header_str(header)
    assert (d == {'contact': '  address: 1,2,3 lane\n  phone: 333-333-4123.',
                  'name': 'Justin L Lorieau'})

    # Entries with colons
    assert (parse_header_str("toc: name: Justin Lorieau") ==
            {'toc': 'name: Justin Lorieau'})
    assert (parse_header_str("""toc: name: Justin Lorieau
    Phone\: xxx-yyy-zzz""") ==
            {'toc': 'name: Justin Lorieau\n    Phone: xxx-yyy-zzz'})

    # Include entries
    header = """
    include:
      src/file1.tex
      src/file2.tex
      src/file 3.tex
    """
    d = parse_header_str(header)
    assert ( d == {'include':
                    '  src/file1.tex\n  src/file2.tex\n  src/file 3.tex'})

    l = str_to_list(d['include'])
    assert l == ['src/file1.tex', 'src/file2.tex', 'src/file 3.tex']

    # Target entries
    header = "targets: pdf, tex"
    d = parse_header_str(header)
    assert (d == {'targets': 'pdf, tex'})
    l = str_to_list(d['targets'])
    assert l == ['pdf', 'tex']


def test_load_header():
    """Test the load header function."""

    test = """
    ---
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    ---
    body
    """
    body_attr = settings.body_attr
    context = {body_attr: test}
    load_header(context)

    assert context[body_attr] == '    body\n    '

    assert 'contact' in context
    assert context['contact'] == '  address: 1,2,3 lane\n  phone: 333-333-4123.'

    assert 'name' in context
    assert context['name'] == 'Justin L Lorieau'

    assert 'address' not in context
    assert 'phone' not in context
