import pytest

from yaramo.model import (
    Edge,
    Node,
    Route,
    Signal,
    SignalDirection,
    SignalFunction,
    SignalKind,
    Topology,
    Wgs84GeoNode,
)
from yaramo.operations import Split


def test_simple_split():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_4, node_3)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    topology_a, topology_b = Split.split(topology, split_edges={edge_3: 5.0})

    assert len(topology_a.nodes) == len([node_1, node_2, node_3]) + 1  # Plus new track end
    assert len(topology_b.nodes) == len([node_4, node_5, node_6]) + 1  # Plus new track end
    assert len(topology_a.edges) == len([edge_1, edge_2]) + 1  # Plus edge to new track end
    assert len(topology_b.edges) == len([edge_4, edge_5]) + 1  # Plus edge to new track end
    assert node_1.uuid in topology_a.nodes.keys()
    assert node_2.uuid in topology_a.nodes.keys()
    assert node_3.uuid in topology_a.nodes.keys()
    assert node_4.uuid in topology_b.nodes.keys()
    assert node_5.uuid in topology_b.nodes.keys()
    assert node_6.uuid in topology_b.nodes.keys()
    assert edge_1.uuid in topology_a.edges.keys()
    assert edge_2.uuid in topology_a.edges.keys()
    assert edge_3.uuid not in topology_a.edges.keys()
    assert edge_3.uuid not in topology_b.edges.keys()
    assert edge_4.uuid in topology_b.edges.keys()
    assert edge_5.uuid in topology_b.edges.keys()


def test_advanced_split():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_2 = Node(geo_node=Wgs84GeoNode(20, 10))  # Point
    node_3 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_4 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 10))  # Point
    node_6 = Node(geo_node=Wgs84GeoNode(50, 10))
    node_7 = Node(geo_node=Wgs84GeoNode(40, 0))  # Point
    node_8 = Node(geo_node=Wgs84GeoNode(50, 0))
    edge_1 = Edge(node_1, node_2)
    edge_2 = Edge(node_3, node_4)
    edge_3 = Edge(node_4, node_2)
    edge_4 = Edge(node_2, node_5)  # Split edge
    edge_5 = Edge(node_4, node_7)  # Split edge
    edge_6 = Edge(node_5, node_6)
    edge_7 = Edge(node_7, node_8)
    edge_8 = Edge(node_5, node_7)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7, edge_8])

    topology_a, topology_b = Split.split(topology, split_edges={edge_4: 5.0, edge_5: 15.0})

    assert len(topology_a.nodes) == len([node_1, node_2, node_3, node_4]) + 2  # Plus two new track ends
    assert len(topology_b.nodes) == len([node_5, node_6, node_7, node_8]) + 2  # Plus two new track ends
    assert len(topology_a.edges) == len([edge_1, edge_2, edge_3]) + 2  # Plus edge to new track ends
    assert len(topology_b.edges) == len([edge_6, edge_7, edge_8]) + 2  # Plus edge to new track ends
    assert node_1.uuid in topology_a.nodes.keys()
    assert node_2.uuid in topology_a.nodes.keys()
    assert node_3.uuid in topology_a.nodes.keys()
    assert node_4.uuid in topology_a.nodes.keys()
    assert node_5.uuid in topology_b.nodes.keys()
    assert node_6.uuid in topology_b.nodes.keys()
    assert node_7.uuid in topology_b.nodes.keys()
    assert node_8.uuid in topology_b.nodes.keys()
    assert edge_1.uuid in topology_a.edges.keys()
    assert edge_2.uuid in topology_a.edges.keys()
    assert edge_3.uuid in topology_a.edges.keys()
    assert edge_4.uuid not in topology_a.edges.keys()
    assert edge_4.uuid not in topology_b.edges.keys()
    assert edge_5.uuid not in topology_a.edges.keys()
    assert edge_5.uuid not in topology_b.edges.keys()
    assert edge_6.uuid in topology_b.edges.keys()
    assert edge_7.uuid in topology_b.edges.keys()
    assert edge_8.uuid in topology_b.edges.keys()

# Test, dessen Kanten nicht ausreicht, um zu trennen
# Split mit Elementen, an Split-Kanten
# Transitiver Split
# Test with geo nodes