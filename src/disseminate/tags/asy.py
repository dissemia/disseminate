
"""
Tags to render asymptote (asy) figures and diagrams
"""
from .img import Img


class Asy(Img):
    """The asy tag for inserting asymptote images."""

    active = True
    process_content = False
    in_ext = '.save'
