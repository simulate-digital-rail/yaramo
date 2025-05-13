from itertools import product

from pytest import raises

import yaramo.utils.coordinateconversion
from yaramo.model import DbrefGeoNode, Node, Wgs84GeoNode

from .helper import create_edge, create_node


def coords_str(node: Node):
    return f"({node.geo_node.x}, {node.geo_node.y})"


def test_anschluss():
    base_scenarios = [
        # Base scenarios are defined in "grids", so look at them like
        # looking at a layout (h=head, s=switch, l=left, r=right).
        (  # north to south
            (" h "),
            (" s "),
            ("   "),
            ("r l"),
        ),
        (  # northeast to southwest:
            ("   h"),
            ("  s "),
            ("    "),
            ("rl  "),
        ),
        (  # east to west:
            ("r   "),
            ("  sh"),
            ("l   "),
        ),
        (  # southeast to northwest:
            ("lr  "),
            ("    "),
            ("  s "),
            ("   h"),
        ),
        (  # south to north:
            ("l r"),
            ("   "),
            (" s "),
            (" h "),
        ),
        (  # southwest to northeast:
            ("  lr"),
            ("    "),
            (" s  "),
            ("h   "),
        ),
        (  # west to east:
            ("   l"),
            ("hs  "),
            ("   r"),
        ),
        (  # northwest to southeast:
            ("h   "),
            (" s  "),
            ("    "),
            ("  rl"),
        ),
        (  # curved north to south:
            ("h  "),
            ("s  "),
            ("   "),
            (" rl"),
        ),
        (  # curved east to west:
            ("r   "),
            ("l   "),
            ("  sh"),
        ),
        (  # branch east to west
            ("r  "),
            ("lsh"),
        ),
    ]

    # base scenarios will be "moved around" by some offsets:
    offsets = (0, -1, -2, -3, -4, -5, 100)

    for scenario in base_scenarios:

        # determine coordinates of elements by parsing base scenarios
        for row_i, row in enumerate(scenario):
            for col_i, cell in enumerate(row):
                coords = row_i, col_i
                if cell == " ":
                    continue
                elif cell == "h":
                    hx, hy = coords
                elif cell == "s":
                    sx, sy = coords
                elif cell == "l":
                    lx, ly = coords
                elif cell == "r":
                    rx, ry = coords
                else:
                    assert False, f"test shouldn't get here ({cell})"

        # apply offsets to base scenario, set up nodes and actually test
        for offset_x, offset_y in product(offsets, repeat=2):
            switch = create_node(sx + offset_x, sy + offset_y)

            head = create_node(hx + offset_x, hy + offset_y)
            create_edge(switch, head)
            left = create_node(lx + offset_x, ly + offset_y)
            create_edge(switch, left)
            right = create_node(rx + offset_x, ry + offset_y)
            create_edge(switch, right)

            print(
                "scenario:",
                "\n  head  ",
                coords_str(head),
                "\n  switch",
                coords_str(switch),
                "\n  left  ",
                coords_str(left),
                "\n  right ",
                coords_str(right),
            )

            # finally call the procedure we want to test here
            switch.calc_anschluss_of_all_edges()

            # assert ``calc_anschluss_of_all_nodes`` did what it should
            assert switch.connected_on_head == head, (
                "head node " f"{coords_str(switch.connected_on_head)} incorrect"
            )
            assert switch.connected_on_left == left, (
                "left node " f"{coords_str(switch.connected_on_left)} incorrect"
            )
            assert switch.connected_on_right == right, (
                "right node " f"{coords_str(switch.connected_on_right)} incorrect"
            )


def test_implausible_anschluss():
    """Assert that detection of "Anschluss" (head, left, right) raises
    an exception on really implausible geographies."""
    head = create_node(0, 0)  # layout:
    point = create_node(2, 2)  #      l
    left = create_node(1, 3)  #       s r
    right = create_node(3, 2)  #     h

    point.connected_nodes.extend((head, left, right))

    with raises(Exception) as exception:
        point.calc_anschluss_of_all_nodes()


def test_wgs84_dbref_coordinate_conversion():
    def _test_distance(_dbref_x, _dbref_y, _wgs84_x, _wgs84_y, factor, smaller_as):
        wgs84_geo_node = Wgs84GeoNode(wgs84_x, wgs84_y)
        dbref_geo_node = DbrefGeoNode(dbref_x, dbref_y)
        assert wgs84_geo_node.get_distance_to_other_geo_node(dbref_geo_node) * factor < smaller_as

    # Example 1:
    dbref_x = 4563230.251887853
    dbref_y = 5601992.441701063
    wgs84_x = 50.55025861737121
    wgs84_y = 12.890666340087865

    _test_distance(dbref_x, dbref_y, wgs84_x, wgs84_y, 1000 * 1000, 2)

    # Example 2:
    dbref_x = 4563437.90802
    dbref_y = 5601946.51808
    wgs84_x = 50.54982337298292
    wgs84_y = 12.893588101538324

    _test_distance(dbref_x, dbref_y, wgs84_x, wgs84_y, 1000 * 1000, 2)

    # Example 3: (close-by)
    dbref_x = 4564720.99586
    dbref_y = 5601735.46336
    wgs84_x = 50.5477883
    wgs84_y = 12.9116547

    _test_distance(dbref_x, dbref_y, wgs84_x, wgs84_y, 1, 0.3)
