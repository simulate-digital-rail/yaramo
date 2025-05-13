import pytest

from yaramo.model import (
    Edge,
    EuclideanGeoNode,
    Node,
    Signal,
    SignalDirection,
    SignalFunction,
    SignalKind,
    Topology,
)
from yaramo.operations import Compare, CompareMode, CompareResult


def test_identical_topologies():
    topology = Topology()
    node_1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_4, node_3)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    signal_1 = Signal(
        edge_3, 5, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal_1)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])
    topology.add_signals([signal_1])
    topology.update_edge_lengths()

    compare_modes = [CompareMode.EXACT, CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(
            topology, topology, compare_mode, given_node_matching={node_1: node_1}
        )
        assert result.node_distance == 0.0
        assert result.edge_length_difference == 0.0
        assert result.signal_distance == 0.0


def test_identical_topologies_but_ids():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])
    topology_a.update_edge_lengths()

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_b3 = Node(geo_node=EuclideanGeoNode(12, 0))  # x differs from Node A3
    node_b4 = Node(geo_node=EuclideanGeoNode(20, 3))  # y differs from Node A4
    node_b5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_b6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    edge_b4 = Edge(node_b4, node_b5)
    edge_b5 = Edge(node_b4, node_b6)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])
    topology_b.update_edge_lengths()

    compare_modes = [CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(
            topology_a, topology_b, compare_mode, given_node_matching={node_a1: node_b1}
        )
        assert result.node_distance == 5.0
        assert node_a1 in result.node_matching.element_matching
        assert result.node_matching.element_matching[node_a1] == node_b1
        assert node_a3 in result.node_matching.element_matching
        assert result.node_matching.element_matching[node_a3] == node_b3
        assert edge_a5 in result.edge_matching.element_matching
        assert result.edge_matching.element_matching[edge_a5] == edge_b5


def test_exclude_element_list():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])
    topology_a.update_edge_lengths()

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_b3 = Node(geo_node=EuclideanGeoNode(12, 0))  # x differs from Node A3
    node_b4 = Node(geo_node=EuclideanGeoNode(20, 3))  # y differs from Node A4
    node_b5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_b6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    edge_b4 = Edge(node_b4, node_b5)
    edge_b5 = Edge(node_b4, node_b6)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])
    topology_b.update_edge_lengths()

    compare_modes = [CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(
            topology_a, topology_b, compare_mode, given_node_matching={node_a1: node_b1}, exclude_element_list=[node_b4]
        )
        assert result.node_distance == 2.0
        assert node_a1 in result.node_matching.element_matching
        assert result.node_matching.element_matching[node_a1] == node_b1
        assert node_a3 in result.node_matching.element_matching
        assert result.node_matching.element_matching[node_a3] == node_b3
        assert edge_a5 in result.edge_matching.element_matching
        assert result.edge_matching.element_matching[edge_a5] == edge_b5


def test_edge_diff_and_signal_distance():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a3, node_a4)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    signal_a1 = Signal(
        edge_a3,
        2,
        SignalDirection.IN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="a1",
    )
    edge_a3.signals.append(signal_a1)
    signal_a2 = Signal(
        edge_a3,
        7,
        SignalDirection.IN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="a2",
    )
    edge_a3.signals.append(signal_a2)
    signal_a3 = Signal(
        edge_a3,
        5,
        SignalDirection.GEGEN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="a3",
    )
    edge_a3.signals.append(signal_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])
    topology_a.add_signals([signal_a1, signal_a2, signal_a3])
    topology_a.update_edge_lengths()

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_b3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_b4 = Node(geo_node=EuclideanGeoNode(22, 0))
    node_b5 = Node(geo_node=EuclideanGeoNode(32, 0))
    node_b6 = Node(geo_node=EuclideanGeoNode(32, 10))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)  # Edge is reversed compared to edge_a3
    edge_b4 = Edge(node_b4, node_b5)
    edge_b5 = Edge(node_b4, node_b6)
    signal_b1 = Signal(
        edge_b3,
        8,
        SignalDirection.GEGEN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="b1",
    )
    edge_b3.signals.append(signal_b1)
    signal_b2 = Signal(
        edge_b3,
        4,
        SignalDirection.GEGEN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="b2",
    )
    edge_b3.signals.append(signal_b2)
    signal_b3 = Signal(
        edge_b3,
        6,
        SignalDirection.IN,
        SignalFunction.Block_Signal,
        SignalKind.Hauptsignal,
        name="b3",
    )
    edge_b3.signals.append(signal_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])
    topology_b.add_signals([signal_b1, signal_b2, signal_b3])
    topology_b.update_edge_lengths()

    compare_modes = [CompareMode.ISOMORPHIC]

    for compare_mode in compare_modes:
        result = Compare.compare(
            topology_a, topology_b, compare_mode, given_node_matching={node_a1: node_b1}
        )
        assert result.node_distance == 6.0
        assert result.edge_length_difference == 2.0
        assert edge_a3 in result.edge_matching.element_matching
        assert edge_b3 == result.edge_matching.element_matching[edge_a3]
        assert signal_a1 in result.signal_matching.element_matching
        assert signal_b1 == result.signal_matching.element_matching[signal_a1]
        assert signal_a2 in result.signal_matching.element_matching
        assert signal_b2 == result.signal_matching.element_matching[signal_a2]
        assert signal_a3 in result.signal_matching.element_matching
        assert signal_b3 == result.signal_matching.element_matching[signal_a3]
        assert result.signal_distance == 4.0


def test_exact_matching_with_overlapping_graph():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a3, node_a4)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])
    topology_a.update_edge_lengths()

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0), uuid=node_a1.uuid)
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10), uuid=node_a2.uuid)
    node_b3 = Node(geo_node=EuclideanGeoNode(12, 0), uuid=node_a3.uuid)  # x differs to Node A3
    node_b4 = Node(geo_node=EuclideanGeoNode(20, 1), uuid=node_a4.uuid)  # y differs to Node A3
    node_b5 = Node(geo_node=EuclideanGeoNode(-10, 0))
    node_b6 = Node(geo_node=EuclideanGeoNode(-10, 10))
    edge_b1 = Edge(node_b1, node_b3, uuid=edge_a1.uuid)
    edge_b2 = Edge(node_b2, node_b3, uuid=edge_a2.uuid)
    edge_b3 = Edge(node_b3, node_b4, uuid=edge_a3.uuid)
    edge_b4 = Edge(node_b5, node_b1)
    edge_b5 = Edge(node_b6, node_b1)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5])
    topology_b.update_edge_lengths()

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
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a6 = Node(geo_node=EuclideanGeoNode(30, 10))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_b3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_b4 = Node(geo_node=EuclideanGeoNode(20, 0))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        result = Compare.compare(
            topology_a, topology_b, CompareMode.ISOMORPHIC, given_node_matching={node_a1: node_b1}
        )


def test_non_isomorphic_topologies_same_node_and_edge_count():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a3 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_a5 = Node(geo_node=EuclideanGeoNode(40, 10))
    node_a6 = Node(geo_node=EuclideanGeoNode(40, 0))
    edge_a1 = Edge(node_a1, node_a2)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a2b = Edge(node_a2, node_a3)
    edge_a2b.intermediate_geo_nodes.extend([EuclideanGeoNode(12, 5), EuclideanGeoNode(18, 5)])
    edge_a3 = Edge(node_a3, node_a4)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a4, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a2b, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_b3 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_b4 = Node(geo_node=EuclideanGeoNode(30, 0))
    node_b5 = Node(geo_node=EuclideanGeoNode(13, 5))
    node_b6 = Node(geo_node=EuclideanGeoNode(23, 5))
    edge_b1 = Edge(node_b1, node_b2)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    edge_b4 = Edge(node_b2, node_b5)
    edge_b5 = Edge(node_b3, node_b5)
    edge_b6 = Edge(node_b5, node_b6)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4, node_b5, node_b6])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3, edge_b4, edge_b5, edge_b6])

    with pytest.raises(ValueError):
        result = Compare.compare(
            topology_a, topology_b, CompareMode.ISOMORPHIC, given_node_matching={node_a1: node_b1}
        )


def test_isomorphic_topologies_without_given_node_matching():
    topology_a = Topology()
    node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_b2 = Node(geo_node=EuclideanGeoNode(0, 10))
    node_b3 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_b4 = Node(geo_node=EuclideanGeoNode(20, 0))
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        result = Compare.compare(topology_a, topology_b, CompareMode.ISOMORPHIC)
