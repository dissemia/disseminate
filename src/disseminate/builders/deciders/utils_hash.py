"""
Utilities for hashing string and files.
"""
import pathlib
import hashlib


def hash_items(*items, chunk_size=4096, hashfunc=hashlib.md5, sort=True):
    """Create a unique text string hash from the given item objects.

    Parameters
    ----------
    *items : Tuple[obj, str, bytes, :obj:`pathlib.Path`]
        Items to use in calculating the hash.
    chunk_size : Optional[int]
        When reading the contents of files (from :obj:`pathlib.Path` items),
        read the files in the given number of chunk bytes.
    hashfunc : Optional[func]
        The type of hash to use.
    sort : Optional[bool]
        If True, sort the items before calculating the hash. Enabling this
        option ensures that the items order does not change the hash.

    Returns
    -------
    hashdigest : str
        The hash digest string.
    """

    # Create the hash function
    hashes = list()

    for item in items:
        if isinstance(item, pathlib.Path):
            if item.suffix == '.pdf':
                hashtxt = hash_pdf(item, chunk_size=chunk_size,
                                   hashfunc=hashfunc)
            else:
                hashtxt = hash_file(item, chunk_size=chunk_size,
                                    hashfunc=hashfunc)
            hashes.append(hashtxt)
        elif isinstance(item, bytes):
            hashes.append(hashfunc(item).digest())
        else:
            hashes.append(hashfunc(str(item).encode()).digest())

    if sort:
        hashes = sorted(hashes)

    hashobj = hashfunc()
    for item in hashes:
        hashobj.update(item)
    return hashobj.hexdigest()


def hash_file(filepath, chunk_size, hashfunc):
    """Create a unique hash for the file contents of the given filepath.

    Parameters
    ----------
    filepath : :obj:`pathlib.Path`
        The filepath of the file whose contents will be hashed.
    chunk_size : Optional[int]
        When reading the contents of files (from :obj:`pathlib.Path` items),
        read the files in the given number of chunk bytes.
    hashfunc : Optional[func]
        The type of hash to use.

    Returns
    -------
    hash : bytes
        The hash bytes.
    """
    # Create the hash function
    hashobj = hashfunc()

    # open file for reading in binary mode
    with open(filepath, 'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            chunk = file.read(chunk_size)
            hashobj.update(chunk)
    return hashobj.digest()


def line_splitter(file, newline, chunk_size, tail=None):
    """Given a file object, read its contents in chunks into lines without
    breaking newlines."""
    tail = tail if tail is not None else ''
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            if tail:
                yield tail
            break
        lines = (tail + chunk).split(newline)
        tail = lines.pop(0)
        if lines:
            yield tail
            tail = lines.pop()
            yield from lines


def hash_pdf(filepath, chunk_size, hashfunc,
             startswith=(b'/CreationDate', b'/ModDate', b'/ID')):
    """Create a unique hash for the file contents of the given pdf filepath.

    PDF files are parsed differently because they contain metadata on the
    date created, which may not reflect a change in the actual content of the
    file.

    Parameters
    ----------
    filepath : :obj:`pathlib.Path`
        The filepath of the file whose contents will be hashed.
    chunk_size : Optional[int]
        When reading the contents of files (from :obj:`pathlib.Path` items),
        read the files in the given number of chunk bytes.
    hashfunc : Optional[func]
        The type of hash to use.
    startswith : Optional[Tuple[str]]
        Lines that start with the given bytes will be ignored in the hash.

    Returns
    -------
    hash : bytes
        The hash bytes.
    """
    # Create the hash function
    hashobj = hashfunc()

    # Retrieve the lines from the file
    with open(filepath, 'rb') as file:
        for line in line_splitter(file, newline=b'\n', chunk_size=chunk_size,
                                  tail=b''):
            if any(line.startswith(starter) for starter in startswith):
                continue
            hashobj.update(line)

    return hashobj.digest()
