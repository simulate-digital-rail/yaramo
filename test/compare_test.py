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
    DbrefGeoNode,
)
from yaramo.operations import Compare, CompareMode, CompareResult


def test_identical_topologies():
    topology = Topology()
    node_1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_4 = Node(geo_node=DbrefGeoNode(20, 0))
    node_5 = Node(geo_node=DbrefGeoNode(30, 0))
    node_6 = Node(geo_node=DbrefGeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_4, node_3)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    compare_modes = [CompareMode.EXACT, CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(topology, topology, compare_mode, given_node_matching={node_1: node_1})
        assert result.node_distance == 0.0


def test_identical_topologies_but_ids():
    topology_a = Topology()
    node_a1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_a2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_a3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_a4 = Node(geo_node=DbrefGeoNode(20, 0))
    node_a5 = Node(geo_node=DbrefGeoNode(30, 0))
    node_a6 = Node(geo_node=DbrefGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_b2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_b3 = Node(geo_node=DbrefGeoNode(12, 0))  # x differs from Node A3
    node_b4 = Node(geo_node=DbrefGeoNode(20, 3))  # y differs from Node A4
    node_b5 = Node(geo_node=DbrefGeoNode(30, 0))
    node_b6 = Node(geo_node=DbrefGeoNode(30, 10))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    edge_b4 = Edge(node_b4, node_b5)
    edge_b5 = Edge(node_b4, node_b6)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])

    compare_modes = [CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(topology_a, topology_b, compare_mode, given_node_matching={node_a1: node_b1})
        assert result.node_distance == 5.0
        assert node_a1 in result.node_matching.element_matching
        assert result.node_matching.element_matching[node_a1] == node_b1


def test_exact_matching_with_overlapping_graph():
    topology_a = Topology()
    node_a1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_a2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_a3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_a4 = Node(geo_node=DbrefGeoNode(20, 0))
    node_a5 = Node(geo_node=DbrefGeoNode(30, 0))
    node_a6 = Node(geo_node=DbrefGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a3, node_a4)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=DbrefGeoNode(0, 0), uuid=node_a1.uuid)
    node_b2 = Node(geo_node=DbrefGeoNode(0, 10), uuid=node_a2.uuid)
    node_b3 = Node(geo_node=DbrefGeoNode(12, 0), uuid=node_a3.uuid)  # x differs to Node A3
    node_b4 = Node(geo_node=DbrefGeoNode(20, 1), uuid=node_a4.uuid)  # y differs to Node A3
    node_b5 = Node(geo_node=DbrefGeoNode(-10, 0))
    node_b6 = Node(geo_node=DbrefGeoNode(-10, 10))
    edge_b1 = Edge(node_b1, node_b3, uuid=edge_a1.uuid)
    edge_b2 = Edge(node_b2, node_b3, uuid=edge_a2.uuid)
    edge_b3 = Edge(node_b3, node_b4, uuid=edge_a3.uuid)
    edge_b4 = Edge(node_b5, node_b1)
    edge_b5 = Edge(node_b6, node_b1)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])
    result = Compare.compare(topology_a, topology_b, CompareMode.EXACT)

    assert result.node_distance == 3.0
    assert node_a1 in result.node_matching.element_matching
    assert node_b1 == result.node_matching.element_matching[node_a1]
    assert node_a2 in result.node_matching.element_matching
    assert node_b2 == result.node_matching.element_matching[node_a2]
    assert node_a5 in result.node_matching.not_found_in_b
    assert node_a6 in result.node_matching.not_found_in_b
    assert node_b5 in result.node_matching.not_found_in_a
    assert node_b6 in result.node_matching.not_found_in_a


def test_non_isomorphic_topologies_different_node_and_edge_count():
    topology_a = Topology()
    node_a1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_a2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_a3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_a4 = Node(geo_node=DbrefGeoNode(20, 0))
    node_a5 = Node(geo_node=DbrefGeoNode(30, 0))
    node_a6 = Node(geo_node=DbrefGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_b2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_b3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_b4 = Node(geo_node=DbrefGeoNode(20, 0))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        result = Compare.compare(topology_a, topology_b, CompareMode.ISOMORPHIC, given_node_matching={node_a1: node_b1})


def test_non_isomorphic_topologies_same_node_and_edge_count():
    topology_a = Topology()
    node_a1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_a2 = Node(geo_node=DbrefGeoNode(10, 0))
    node_a3 = Node(geo_node=DbrefGeoNode(20, 0))
    node_a4 = Node(geo_node=DbrefGeoNode(30, 0))
    node_a5 = Node(geo_node=DbrefGeoNode(40, 10))
    node_a6 = Node(geo_node=DbrefGeoNode(40, 0))
    edge_a1 = Edge(node_a1, node_a2)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a2b = Edge(node_a2, node_a3)
    edge_a2b.intermediate_geo_nodes.extend([DbrefGeoNode(12, 5), DbrefGeoNode(18, 5)])
    edge_a3 = Edge(node_a3, node_a4)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a2b, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_b2 = Node(geo_node=DbrefGeoNode(10, 0))
    node_b3 = Node(geo_node=DbrefGeoNode(20, 0))
    node_b4 = Node(geo_node=DbrefGeoNode(30, 0))
    node_b5 = Node(geo_node=DbrefGeoNode(13, 5))
    node_b6 = Node(geo_node=DbrefGeoNode(23, 5))
    edge_b1 = Edge(node_b1, node_b2)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    edge_b4 = Edge(node_b2, node_b5)
    edge_b5 = Edge(node_b3, node_b5)
    edge_b6 = Edge(node_b5, node_b6)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5, edge_b6])

    with pytest.raises(ValueError):
        result = Compare.compare(topology_a, topology_b, CompareMode.ISOMORPHIC, given_node_matching={node_a1: node_b1})


def test_isomorphic_topologies_without_given_node_matching():
    topology_a = Topology()
    node_a1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_a2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_a3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_a4 = Node(geo_node=DbrefGeoNode(20, 0))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_b2 = Node(geo_node=DbrefGeoNode(0, 10))
    node_b3 = Node(geo_node=DbrefGeoNode(10, 0))
    node_b4 = Node(geo_node=DbrefGeoNode(20, 0))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        result = Compare.compare(topology_a, topology_b, CompareMode.ISOMORPHIC)
