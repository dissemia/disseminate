import pathlib

import pytest

from disseminate.tags.data import DelimData


class DelimDataFixture(DelimData):
    """A new DelimData tag that holds a strong reference to the context"""
    context = None
    aliases = tuple()


@pytest.fixture
def csv_tag1(context_cls):
    """An @csv tag from data with a header"""
    paths = [pathlib.Path('.')]
    context = context_cls(paths=paths)

    # 1. Test the parsing of text strings with header
    text1 = ("header 1, header 2, header 3\n"
             "1-1, 1-2, 1-3\n"
             "2-1, 2-2, 2-3\n"
             "3-1, 3-2, 3-3\n")

    data = DelimDataFixture(name='csv', content=text1, attributes='',
                            context=context)

    return data


@pytest.fixture
def csv_tag2(context_cls):
    """An @csv tag from data without a header"""
    paths = [pathlib.Path('.')]
    context = context_cls(paths=paths)

    # 1. Test the parsing of text strings with header
    text1 = ("1, 2, 3\n"
             "4, 5, 6\n"
             "7, 8, 9\n")

    data = DelimDataFixture(name='csv', content=text1, attributes='noheader',
                            context=context)

    return data


@pytest.fixture
def csv_tag3(context_cls):
    """An @csv tag from data with a header and disseminate formatting"""
    paths = [pathlib.Path('.')]
    context = context_cls(paths=paths)

    # 1. Test the parsing of text strings with header
    text1 = ("header @i{1}, header @i{2}, header @i{3}\n"
             "My @b{1-1} column, My @b{1-2} column, My @b{1-3} column\n"
             "My @b{2-1} column, My @b{2-2} column, My @b{2-3} column\n"
             "My @b{3-1} column, My @b{3-2} column, My @b{3-3} column\n")

    data = DelimDataFixture(name='csv', content=text1, attributes='',
                            context=context)

    return data
