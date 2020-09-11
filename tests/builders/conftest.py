"""
Utility fixtures for builder tests.
"""
import xml.dom.minidom

import pytest


@pytest.fixture
def is_svg():
    """Returns true if the given filepath is a valid svg file."""
    def _is_svg(filepath):
        # Load the svg file as xml
        with xml.dom.minidom.parse(str(filepath)) as dom:
            # See if there are svg tags in the xml
            return any(node.tagName == 'svg' or node.tagName == 'SVG'
                       for node in dom.childNodes)
    return _is_svg


@pytest.fixture
def svg_dims():
    """Checks whether the svg filepath matches the given width and/or the
    given height."""
    def _svg_dims(filepath, width=None, height=None, abs=0.1):
        # Load the svg file as xml
        with xml.dom.minidom.parse(str(filepath)) as dom:
            # find the svg tag
            svg_nodes = [node for node in dom.childNodes
                         if node.tagName == 'svg']
            if len(svg_nodes) == 0:
                return None

            svg_node = svg_nodes[0]
            svg_width = svg_node.getAttribute('width') or None
            svg_height = svg_node.getAttribute('height') or None
            print('svg dimensions:', svg_width, svg_height)

            is_matched = True
            for dim, svg_dim in ((width, svg_width), (height, svg_height)):
                if dim is None:  # skip test if not specified
                    continue

                if svg_dim is None:  # svg doesn't have this dimension
                    is_matched &= False
                    continue

                if 'px' in svg_dim:
                    svg_dim = float(svg_dim.strip('px'))
                    dim = float(dim.strip('px'))

                elif 'pt' in svg_dim:
                    svg_dim = float(svg_dim.strip('pt'))
                    dim = float(dim.strip('pt'))

                is_matched &= (svg_dim == pytest.approx(dim, abs=abs))

            return is_matched
    return _svg_dims
