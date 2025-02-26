from yaramo.edge import Edge
from yaramo.geo_node import DbrefGeoNode
from yaramo.node import Node
from yaramo.topology import Topology

import pytest

@pytest.fixture
def straight_track():
    node1 = Node()
    node2 = Node()
    node3 = Node()

    edge1 = Edge(node1, node2, length=100)
    edge2 = Edge(node2, node3, length=100)

    node1.set_connection_head(node2)
    node2.set_connection_head(node3)
    node2.connected_nodes.append(node1)
    node3.connected_nodes.append(node2)

    topology = Topology()
    topology.add_node(node1)
    topology.add_node(node2)
    topology.add_node(node3)
    topology.add_edge(edge1)
    topology.add_edge(edge2)

    return topology


@pytest.fixture
def switch():
    node1 = Node()
    switch = Node()
    node2 = Node()
    node3 = Node()

    node1.geo_node = DbrefGeoNode(0, 10)
    switch.geo_node = DbrefGeoNode(50, 10)
    node2.geo_node = DbrefGeoNode(100, 10)
    node3.geo_node = DbrefGeoNode(100, 20)

    edge1 = Edge(node1, switch, length=50)
    edge2 = Edge(switch, node2, length=50)
    edge3 = Edge(switch, node3, length=50)

    node1.set_connection_head(switch)
    switch.set_connection_head(node2)
    switch.set_connection_left(node3)

    switch.connected_nodes.append(node1)
    node2.connected_nodes.append(switch)
    node3.connected_nodes.append(switch)

    topology = Topology()
    topology.add_node(node1)
    topology.add_node(switch)
    topology.add_node(node2)
    topology.add_node(node3)
    topology.add_edge(edge1)
    topology.add_edge(edge2)
    topology.add_edge(edge3)

    return topology


if __name__ == "__main__":
    straight_track()
    switch()



def test_detect_switch(switch):
    topology = switch

    switch_count = 0

    for node in topology.nodes.values():
        if node.is_switch():
            switch_count += 1

    assert switch_count == 1


def test_dont_detect_straight(straight_track):
    topology = straight_track

    switch_count = 0

    for node in topology.nodes.values():
        if node.is_switch():
            switch_count += 1

    assert switch_count == 0
