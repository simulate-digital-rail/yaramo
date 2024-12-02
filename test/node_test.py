from itertools import product

from pytest import raises

from yaramo.geo_node import Wgs84GeoNode
from yaramo.node import Node


def create_node(x, y):
    return Node(geo_node=Wgs84GeoNode(x, y))


def coords_str(node: Node):
    return f"({node.geo_node.geo_point.x}, {node.geo_node.geo_point.y})"


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
            head = create_node(hx + offset_x, hy + offset_y)
            switch = create_node(sx + offset_x, sy + offset_y)
            left = create_node(lx + offset_x, ly + offset_y)
            right = create_node(rx + offset_x, ry + offset_y)

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

            # connect all nodes to the switch
            switch.connected_nodes.extend((head, left, right))

            # finally call the procedure we want to test here
            switch.calc_anschluss_of_all_nodes()

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
    switch = create_node(2, 2)  #      l
    left = create_node(1, 3)  #       s r
    right = create_node(3, 2)  #     h

    switch.connected_nodes.extend((head, left, right))

    with raises(Exception) as exception:
        switch.calc_anschluss_of_all_nodes()
