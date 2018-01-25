
from .core import Tag



class Chapter(Tag):

    def process_ast(self, target):
        # return <h1> for html


class HTMLHeading(Tag):

    id = None

    def __init__(self, id=None, *args, **kwargs):

class H1(HTMLHeading):  pass

class H2(HTMLHeading): pass

class H3(HTMLHeading): pass

class H4(HTMLHeading): pass

class H5(HTMLHeading): pass

class H5(HTMLHeading): pass