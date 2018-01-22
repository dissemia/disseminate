def print_ast(ast, level=1):
    """Pretty print an AST with one entry per line and indentation for nested
    levels."""
    assert isinstance(ast, list)

    print()
    for count, item in enumerate(ast, 1):
        if isinstance(item, str):
            print("{}.{}:".format(level, count),
                  "  " * level, repr(item))
            continue

        if (hasattr(item, 'tag_content')
            and not isinstance(item.tag_content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item)

        if (hasattr(item, 'tag_content')
            and isinstance(item.tag_content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item.tag_type, "{")
            print_ast(item.tag_content, level + 1)
            print("    " + "  " * level + "}")
