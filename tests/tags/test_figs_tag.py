"""
Tests for the figure tags.
"""
from disseminate.ast import process_ast


def test_marginfig_parsing():
    """Test the parsing of marginfig tags."""

    test1 = "@marginfig{fig1}"
    root = process_ast(test1)
    assert root.content.name == 'marginfig'
    assert root.content.content == 'fig1'

    test2 = "@marginfig{{fig1}}"
    root = process_ast(test2)
    assert root.content.name == 'marginfig'
    assert root.content.content == '{fig1}'
