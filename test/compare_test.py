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
from yaramo.operations import Compare, CompareMode, CompareResult


def test_identical_topologies():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_4, node_3)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    compare_modes = [CompareMode.EXACT, CompareMode.EXACT_BUT_IDS, CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(topology, topology, compare_mode)
        assert result.comparability_degree == 1.0
