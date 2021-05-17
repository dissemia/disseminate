"""
Test the html scanner
"""
from disseminate.builders.scanners.scanner import Scanner
from disseminate.builders.scanners.html_scanner import HtmlScanner
from disseminate.paths import SourcePath


def test_html_scan():
    """Test the html scan function."""
    html_scan = HtmlScanner.scan_function

    # Files work
    assert (['/media/css/default.css'] ==
            html_scan('<link rel="stylesheet" href="/media/css/default.css">'))

    # But urls with protocols don't
    assert ([] ==
            html_scan('<link rel="stylesheet" href="https://test.com/">'))


def test_html_scanner_scan():
    """Test the scan method of the HtmlScanner."""

    # 1. Test scan with the templates/default
    project_root = 'src/disseminate/templates/default/html'
    template_filepath = SourcePath(project_root=project_root,
                                   subpath='template.html')
    html_scanner = HtmlScanner

    # Test the dependent files
    infilepaths = html_scanner.scan(template_filepath)

    assert len(infilepaths) == 4

    # Check each file
    assert infilepaths[0].match('templates/default/html/'
                                'media/css/bootstrap.min.css')
    assert infilepaths[0].project_root.match('templates/default/html/')
    assert infilepaths[0].subpath.match('media/css/bootstrap.min.css')

    assert infilepaths[1].match('templates/default/html/media/css/base.css')
    assert infilepaths[1].project_root.match('templates/default/html/')
    assert infilepaths[1].subpath.match('media/css/base.css')

    assert infilepaths[2].match('templates/default/html/'
                                'media/css/default.css')
    assert infilepaths[2].project_root.match('templates/default/html/')
    assert infilepaths[2].subpath.match('media/css/default.css')

    assert infilepaths[3].match('templates/default/html/media/css/'
                                'pygments.css')
    assert infilepaths[3].project_root.match('templates/default/html/')
    assert infilepaths[3].subpath.match('media/css/pygments.css')

    # Likewise, the base scanner works to parse html
    scanner = Scanner
    infilepaths2 = scanner.scan(template_filepath)

    assert infilepaths == infilepaths2
