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
    assert (html_scan('<link rel="stylesheet" href="/media/css/default.css">')
            == ['/media/css/default.css'])

    # But urls with protocols don't
    assert (html_scan('<link rel="stylesheet" href="https://test.com/">')
            == [])


def test_html_scanner_scan():
    """Test the scan method of the HtmlScanner."""

    # 1. Test scan with the templates/default
    project_root = 'src/disseminate/templates/default'
    template_filepath = SourcePath(project_root=project_root,
                                   subpath='template.html')
    html_scanner = HtmlScanner

    # Test the dependent files
    infilepaths = html_scanner.scan(template_filepath)

    assert len(infilepaths) == 4

    # Check each file
    assert (str(infilepaths[0]) ==
            'src/disseminate/templates/default/media/css/bootstrap.min.css')
    assert (str(infilepaths[0].project_root) ==
            'src/disseminate/templates/default')
    assert str(infilepaths[0].subpath) == 'media/css/bootstrap.min.css'

    assert (str(infilepaths[1]) ==
            'src/disseminate/templates/default/media/css/base.css')
    assert (str(infilepaths[1].project_root) ==
            'src/disseminate/templates/default')
    assert str(infilepaths[1].subpath) == 'media/css/base.css'

    assert (str(infilepaths[2]) ==
            'src/disseminate/templates/default/media/css/default.css')
    assert (str(infilepaths[2].project_root) ==
            'src/disseminate/templates/default')
    assert str(infilepaths[2].subpath) == 'media/css/default.css'

    assert (str(infilepaths[3]) ==
            'src/disseminate/templates/default/media/css/pygments.css')
    assert (str(infilepaths[3].project_root) ==
            'src/disseminate/templates/default')
    assert str(infilepaths[3].subpath) == 'media/css/pygments.css'

    # Likewise, the base scanner works to parse html
    scanner = Scanner
    infilepaths2 = scanner.scan(template_filepath)

    assert infilepaths == infilepaths2
