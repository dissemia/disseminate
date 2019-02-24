"""
Test the ASTValidator.
"""
import pytest

from disseminate.ast import process_ast
from disseminate.ast.validate import ValidateAndCleanAST, ParseError
from disseminate.tags import Tag


def test_join_strings(context_cls):
    """Test the join_string method of the ValidateAndCleanAST class."""

    context = context_cls()
    validate = ValidateAndCleanAST()

    # Try simple flat lists
    assert validate.join_strings(['a', 'b', 5, 'c', 'd']) == ['ab', 5, 'cd']
    assert validate.join_strings([1, 2, 3, 4]) == [1, 2, 3, 4]

    # Try nested lists
    assert (validate.join_strings(['a', 'b', [1, 2, 3], 'c', 'd']) ==
            ['ab',[1, 2, 3], 'cd'])
    assert (validate.join_strings(['a', 'b', [1, 'c', 'd'], 'e', 'f']) ==
            ['ab', [1, 'cd'], 'ef'])

    # Try with tags non-nested tag
    tag = Tag(name='tag', content='test', attributes=(), context=context)
    assert (validate.join_strings(['a', 'b', tag, 'c', 'd']) ==
            ['ab', tag, 'cd'])

    # Try with nested tags
    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (validate.join_strings(tag) == tag)
    assert tag.content == [1, 'cd']

    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (validate.join_strings([tag]) == [tag])
    assert tag.content == [1, 'cd']

    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (validate.join_strings(['a', 'b', tag, 'c', 'd']) ==
            ['ab', tag, 'cd'])
    assert tag.content == [1, 'cd']

    tag1 = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
               context=context)
    tag2 = Tag(name='tag', content=[tag1, 'c', 'd'], attributes=(),
               context=context)
    assert (validate.join_strings(['a', 'b', tag2, 'c', 'd']) ==
            ['ab', tag2, 'cd'])
    assert tag1.content == [1, 'cd']
    assert tag2.content == [tag1, 'cd']


def test_ast_count(context_cls):
    """Test the assignment of line_numbers in tags."""

    context = context_cls()

    # Setup a test source string
    test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfigtag[offset=-1.0em]{
      @imgtag{media/files}
      @captiontag{This is my @i{first} figure.}
    }

    This is a @13C variable.

    Here is a @i{new} paragraph."""

    # Parse it
    ast = process_ast(test, context=context)

    # Check the line numbers of tags.
    assert ast[1].line_number == 4  # @b tag
    assert ast[3].line_number == 5  # @marginfigtag
    assert ast[3][1].line_number == 6  # @imgtag
    assert ast[3][3].line_number == 7  # @captiontag
    assert ast[3][3][1].line_number == 7  # @i tag
    assert ast[5].line_number == 10  # @13C tag
    assert ast[7].line_number == 12  # @13C tag


def test_ast_validation(context_cls):
    """Test the correct validation when parsing an AST."""

    context = context_cls()

    # Test an invalid tag with a root-level tag
    test_invalid = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @caption{This is my @i{first} figure.}
    """

    # Process a string with an open tag
    with pytest.raises(ParseError) as e:
        ast = process_ast(test_invalid, context=context)

    # The error should pop up in line 5
    assert "line 5" in str(e.value)

    # Test an invalid tag with a nested tag
    test_invalid2 = """
            This is my test document. It has multiple paragraphs.

            Here is a new one with @b{bolded} text as an example.
            @marginfigtag[offset=-1.0em]{
              @imgtag{media/files}
              @caption{This is my @i{first figure.}
              }
        """

    # Process a string with an open tag
    with pytest.raises(ParseError) as e:
        ast = process_ast(test_invalid2, context=context)

    # The error should pop up in line 5
    assert "line 5" in str(e.value)


def test_ast_validation_cases(context_cls):
    """Test specific cases of AST validation"""

    context = context_cls()

    valid1 = """
    @tag{
     y &= & \\int_a^b{x} && \\mathrm{(first equation)}
     }
    """

    ast1 = process_ast(valid1, context=context)

    assert ast1.name == 'root'
    assert ast1.content[1].name == 'tag'
    assert ast1.content[1].content == ('\n     y &= & \\int_a^b{x} && '
                                       '\\mathrm{(first equation)}\n     ')
