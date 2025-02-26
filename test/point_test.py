import pytest

from yaramo.edge import Edge
from yaramo.geo_node import DbrefGeoNode
from yaramo.node import Node
from yaramo.topology import Topology

from .helper import create_node


@pytest.fixture
def straight_track():
    # Note that this kind of topology shouldn't exist
    node1 = Node()
    node2 = Node()
    node3 = Node()

    edge1 = Edge(node1, node2, length=100)
    edge2 = Edge(node2, node3, length=100)

    topology = Topology()
    topology.add_node(node1)
    topology.add_node(node2)
    topology.add_node(node3)
    topology.add_edge(edge1)
    topology.add_edge(edge2)

    return topology


@pytest.fixture
def point():
    node1 = create_node(0, 10)
    point = create_node(50, 10)
    node2 = create_node(100, 10)
    node3 = create_node(100, 20)

    edge1 = Edge(node1, point, length=50)
    edge2 = Edge(point, node2, length=50)
    edge3 = Edge(point, node3, length=50)

    topology = Topology()
    topology.add_node(node1)
    topology.add_node(point)
    topology.add_node(node2)
    topology.add_node(node3)
    topology.add_edge(edge1)
    topology.add_edge(edge2)
    topology.add_edge(edge3)

    return topology


if __name__ == "__main__":
    straight_track()
    point()


def test_detect_switch(point):
    topology = point

    point_count = 0

    for node in topology.nodes.values():
        if node.is_point():
            point_count += 1

    assert point_count == 1


def test_dont_detect_straight(straight_track):
    topology = straight_track

    point_count = 0

    for node in topology.nodes.values():
        if node.is_point():
            point_count += 1

    assert point_count == 0
