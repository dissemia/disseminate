"""
Test the processing of hashes in tags
"""

from disseminate.tags import Tag


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @myfig[offset=-1.0em]{
      @myimg{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, an @15N, and a @H2O macro. but this is an email
    address: justin@lorieau.com

    Here is a new paragraph."""


def test_process_hash(context):
    """Test the process_hash function."""

    # 1. Test a reference example
    # Process the body tag and check it
    body = Tag(name='body', content=test, attributes='', context=context)
    assert body.hash == 'e0ac309529'

    # The tag is otherwise accurately processed.
    assert isinstance(body.content, list)

    body = Tag(name='body', content=test + 'a', attributes='', context=context)
    assert body.hash == '25a686d9f0'
