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
    DbrefGeoNode
)
from yaramo.operations import Label, Split


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

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    assert len(topology_a.nodes) == len([node_1, node_2, node_3]) + 1  # Plus new track end
    assert len(topology_b.nodes) == len([node_4, node_5, node_6]) + 1  # Plus new track end
    assert len(topology_a.edges) == len([edge_1, edge_2]) + 1  # Plus edge to new track end
    assert len(topology_b.edges) == len([edge_4, edge_5]) + 1  # Plus edge to new track end
    assert [node_1, node_2, node_3, edge_1, edge_2] in topology_a
    assert [node_4, node_5, node_6, edge_4, edge_5] in topology_b
    assert edge_3 not in topology_a
    assert edge_3 not in topology_b


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

    topology_a, topology_b, _ = Split.split(
        topology,
        split_edges={edge_4: 5.0, edge_5: 15.0},
        node_label_assignments={node_1: Label.A_Topology},
    )

    assert (
        len(topology_a.nodes) == len([node_1, node_2, node_3, node_4]) + 2
    )  # Plus two new track ends
    assert (
        len(topology_b.nodes) == len([node_5, node_6, node_7, node_8]) + 2
    )  # Plus two new track ends
    assert len(topology_a.edges) == len([edge_1, edge_2, edge_3]) + 2  # Plus edge to new track ends
    assert len(topology_b.edges) == len([edge_6, edge_7, edge_8]) + 2  # Plus edge to new track ends
    assert [node_1, node_2, node_3, node_4, edge_1, edge_2, edge_3] in topology_a
    assert [node_5, node_6, node_7, node_8, edge_6, edge_7, edge_8] in topology_b
    assert edge_4 not in topology_a
    assert edge_4 not in topology_b
    assert edge_5 not in topology_a
    assert edge_5 not in topology_b


def test_invalid_split_edge_length():
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

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(topology, split_edges={edge_3: 20.0})


def test_invalid_split_edge_length_zero():
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

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(topology, split_edges={edge_3: 0.0})


def test_invalid_split_edge_length_negative():
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

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(topology, split_edges={edge_3: -5.0})


def test_invalid_split_on_signal():
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
    signal = Signal(
        edge_3, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])
    topology.add_signals([signal])

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(topology, split_edges={edge_3: 5.0})


def test_invalid_split_not_enough_edges():
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

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(topology, split_edges={edge_4: 5.0})


def test_split_in_three_partitions():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(40, 10))  # Point
    node_7 = Node(geo_node=Wgs84GeoNode(50, 10))
    node_8 = Node(geo_node=Wgs84GeoNode(50, 20))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_6, node_4)
    edge_6 = Edge(node_6, node_7)
    edge_7 = Edge(node_6, node_8)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7])

    topology_a, topology_b, _ = Split.split(topology, split_edges={edge_3: 5.0, edge_5: 5.0})
    assert [
        node_1,
        node_2,
        node_3,
        node_6,
        node_7,
        node_8,
        edge_1,
        edge_2,
        edge_6,
        edge_7,
    ] in topology_a
    assert [node_4, node_5, edge_4] in topology_b


def test_split_in_more_than_three_partitions():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))  # Point
    node_6 = Node(geo_node=Wgs84GeoNode(40, 10))  # Point
    node_7 = Node(geo_node=Wgs84GeoNode(50, 10))
    node_8 = Node(geo_node=Wgs84GeoNode(50, 20))
    node_9 = Node(geo_node=Wgs84GeoNode(50, 5))
    node_A = Node(geo_node=Wgs84GeoNode(50, 0))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_6, node_4)
    edge_6 = Edge(node_6, node_7)
    edge_7 = Edge(node_6, node_8)
    edge_8 = Edge(node_5, node_9)
    edge_9 = Edge(node_5, node_A)
    topology.add_nodes(
        [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_A]
    )
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7, edge_8, edge_9])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0, edge_5: 5.0, edge_4: 5.0}
    )
    assert [node_1, node_2, node_3, node_5, node_6, node_7, node_8, node_9, node_A] in topology_a
    assert [node_4] in topology_b
    assert [edge_1, edge_2, edge_6, edge_7, edge_8, edge_9] in topology_a
    # No predefined edges are left in topology B due to split edges


def test_add_non_connected_elements_to_a_partition():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    node_b1 = Node(geo_node=Wgs84GeoNode(100, 0))
    node_b2 = Node(geo_node=Wgs84GeoNode(110, 0))  # Point
    node_b3 = Node(geo_node=Wgs84GeoNode(120, 0))
    node_b4 = Node(geo_node=Wgs84GeoNode(120, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    edge_b1 = Edge(node_b1, node_b2)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b2, node_b4)
    topology.add_nodes(
        [node_1, node_2, node_3, node_4, node_5, node_6, node_b1, node_b2, node_b3, node_b4]
    )
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_b1, edge_b2, edge_b3])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0}, add_missing_elements_to_topology=Label.A_Topology
    )

    assert [node_1, node_2, node_3, node_b1, node_b2, node_b3, node_b4] in topology_a
    assert [node_4, node_5, node_6] in topology_b
    assert [edge_1, edge_2, edge_b1, edge_b2, edge_b3] in topology_a
    assert [edge_4, edge_5] in topology_b


def test_elements_on_split_edges():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    signal_1 = Signal(
        edge_1, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_1.signals.append(signal_1)
    signal_2 = Signal(
        edge_3, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal_2)
    signal_3 = Signal(
        edge_5, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_5.signals.append(signal_3)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])
    topology.add_signals([signal_1, signal_2, signal_3])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 7.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    assert len(topology_a.signals) == 2
    assert signal_1 in topology_a
    assert signal_2 in topology_a
    assert len(topology_b.signals) == 1
    assert signal_3 in topology_b


def test_transitive_split():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(40, 10))  # Point
    node_7 = Node(geo_node=Wgs84GeoNode(50, 10))
    node_8 = Node(geo_node=Wgs84GeoNode(50, 20))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    edge_6 = Edge(node_6, node_7)
    edge_7 = Edge(node_6, node_8)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7])
    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    topology_b, topology_c, _ = Split.split(
        topology_b, split_edges={edge_5: 10.0}, node_label_assignments={node_4: Label.A_Topology}
    )

    expected_nodes_in_a = [node_1, node_2, node_3]  # Plus one split node
    expected_edges_in_a = [edge_1, edge_2]  # Plus one split edge
    expected_nodes_in_b = [node_4, node_5]  # Plus two split nodes
    expected_edges_in_b = [edge_4]  # Plus two split edges
    expected_nodes_in_c = [node_6, node_7, node_8]  # Plus one split node
    expected_edges_in_c = [edge_6, edge_7]  # Plus one split edge

    assert len(topology_a.nodes) == len(expected_nodes_in_a) + 1
    assert len(topology_a.edges) == len(expected_edges_in_a) + 1
    assert len(topology_b.nodes) == len(expected_nodes_in_b) + 2
    assert len(topology_b.edges) == len(expected_edges_in_b) + 2
    assert len(topology_c.nodes) == len(expected_nodes_in_c) + 1
    assert len(topology_c.edges) == len(expected_edges_in_c) + 1

    assert expected_nodes_in_a in topology_a
    assert expected_edges_in_a in topology_a
    assert expected_nodes_in_b in topology_b
    assert expected_edges_in_b in topology_b
    assert expected_nodes_in_c in topology_c
    assert expected_edges_in_c in topology_c


def test_geo_node_split():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(30, 30))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 40))
    node_6 = Node(geo_node=Wgs84GeoNode(40, 40))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)

    edge_3 = Edge(node_3, node_4)
    edge_3.intermediate_geo_nodes.extend(
        [Wgs84GeoNode(16, 3), Wgs84GeoNode(22, 10), Wgs84GeoNode(27, 24)]
    )

    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 32.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    def _count_geo_node(_topology: Topology):
        return sum(map(lambda _edge: len(_edge.intermediate_geo_nodes), _topology.edges.values()))

    assert _count_geo_node(topology_a) == 2
    assert _count_geo_node(topology_b) == 1


def test_route_split():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)

    # Route 1
    signal_1 = Signal(
        edge_1, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_1.signals.append(signal_1)
    signal_2 = Signal(
        edge_3, 3.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal_2)
    route_1 = Route(signal_1)
    route_1.edges.add(edge_1)
    route_1.edges.add(edge_3)
    route_1.end_signal = signal_2

    # Route 2
    signal_3 = Signal(
        edge_3, 7.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal_3)
    signal_4 = Signal(
        edge_4, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_4.signals.append(signal_4)
    route_2 = Route(signal_3)
    route_2.edges.add(edge_3)
    route_2.edges.add(edge_4)
    route_2.end_signal = signal_4

    # Route 3
    signal_5 = Signal(
        edge_4, 3.0, SignalDirection.GEGEN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_4.signals.append(signal_5)
    signal_6 = Signal(
        edge_1, 3.0, SignalDirection.GEGEN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_1.signals.append(signal_6)
    route_3 = Route(signal_5)
    route_3.edges.add(edge_4)
    route_3.edges.add(edge_3)
    route_3.edges.add(edge_1)
    route_3.end_signal = signal_6

    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])
    topology.add_signals([signal_1, signal_2, signal_3, signal_4, signal_5, signal_6])
    topology.add_routes([route_1, route_2, route_3])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    # Note: route 3 goes over split edge, so it gets removed
    assert len(topology_a.routes) == 1
    assert route_1 in topology_a
    assert len(topology_a.signals) == 3
    assert len(topology_b.routes) == 1
    assert route_2 in topology_b
    assert len(topology_b.signals) == 3

def test_route_split_three_parts():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))  # Point
    node_7 = Node(geo_node=Wgs84GeoNode(40, 10))
    node_8 = Node(geo_node=Wgs84GeoNode(40, 20))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    edge_6 = Edge(node_6, node_7)
    edge_7 = Edge(node_6, node_8)

    # Route 1
    signal_1 = Signal(
        edge_1, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_1.signals.append(signal_1)
    signal_2 = Signal(
        edge_7, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_7.signals.append(signal_2)
    route_1 = Route(signal_1)
    route_1.edges.add(edge_1)
    route_1.edges.add(edge_3)
    route_1.edges.add(edge_5)
    route_1.edges.add(edge_7)
    route_1.end_signal = signal_2

    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7])
    topology.add_signals([signal_1, signal_2])
    topology.add_routes([route_1])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0, edge_5: 5.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    # Note: route 1 goes over split area, so it gets removed
    assert len(topology_a.routes) == 0
    assert len(topology_b.routes) == 0

def test_route_ends_on_split_edge():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)

    # Route 1
    signal_1 = Signal(
        edge_1, 5.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_1.signals.append(signal_1)
    signal_2 = Signal(
        edge_3, 2.0, SignalDirection.IN, SignalFunction.Block_Signal, SignalKind.Hauptsignal
    )
    edge_3.signals.append(signal_2)
    route_1 = Route(signal_1)
    route_1.edges.add(edge_1)
    route_1.edges.add(edge_3)
    route_1.end_signal = signal_2

    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])
    topology.add_signals([signal_1, signal_2])
    topology.add_routes([route_1])

    topology_a, topology_b, _ = Split.split(
        topology, split_edges={edge_3: 5.0}, node_label_assignments={node_1: Label.A_Topology}
    )

    assert len(topology_a.routes) == 1
    assert route_1 in topology_a
    assert list(route_1.edges) in topology_a
    assert len(route_1.edges) == 2
    assert len(topology_b.routes) == 0


def test_new_end_nodes():
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

    topology_a, topology_b, new_end_nodes_matching = Split.split(
        topology, split_edges={edge_3: 5.0}
    )
    for split_edge, new_end_nodes in new_end_nodes_matching.items():
        assert split_edge not in topology_a
        assert split_edge not in topology_b
        assert new_end_nodes[0] in topology_a
        assert new_end_nodes[1] in topology_b
        assert new_end_nodes[0] not in topology_b
        assert new_end_nodes[1] not in topology_a


def test_assign_nodes_to_labels():
    labels_of_node_1 = [Label.A_Topology, Label.B_Topology]
    for label_of_node_1 in labels_of_node_1:
        topology = Topology()
        node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
        node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
        node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
        node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
        node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
        node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
        edge_1 = Edge(node_1, node_3)
        edge_2 = Edge(node_2, node_3)
        edge_3 = Edge(node_3, node_4)
        edge_4 = Edge(node_4, node_5)
        edge_5 = Edge(node_4, node_6)
        topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
        topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

        topology_a, topology_b, _ = Split.split(
            topology, split_edges={edge_3: 5.0}, node_label_assignments={node_1: label_of_node_1}
        )
        if label_of_node_1 == Label.A_Topology:
            assert node_1 in topology_a
        else:
            assert node_1 in topology_b


def test_assign_nodes_to_labels_conflicting_label():
    topology = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 0))
    node_6 = Node(geo_node=Wgs84GeoNode(30, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)
    edge_5 = Edge(node_4, node_6)
    topology.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            split_edges={edge_3: 5.0},
            node_label_assignments={node_1: Label.A_Topology, node_2: Label.B_Topology},
        )


def test_five_parts_after_split():
    labels_of_selected_nodes = [Label.A_Topology, Label.B_Topology]
    for losn in labels_of_selected_nodes:
        topology = Topology()
        node_1 = Node(geo_node=Wgs84GeoNode(0, 5))
        node_2 = Node(geo_node=Wgs84GeoNode(0, 0))
        node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
        node_4 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
        node_5 = Node(geo_node=Wgs84GeoNode(30, 5))
        node_6 = Node(geo_node=Wgs84GeoNode(30, 0))  # Point
        node_7 = Node(geo_node=Wgs84GeoNode(40, 0))  # Point
        node_8 = Node(geo_node=Wgs84GeoNode(50, 0))  # Point
        node_9 = Node(geo_node=Wgs84GeoNode(60, 5))
        node_10 = Node(geo_node=Wgs84GeoNode(60, 0))
        edge_1 = Edge(node_1, node_3)
        edge_2 = Edge(node_2, node_3)
        edge_3 = Edge(node_4, node_3)
        edge_4 = Edge(node_4, node_5)
        edge_5 = Edge(node_4, node_6)
        edge_6 = Edge(node_7, node_6)
        edge_7 = Edge(
            node_6, node_7, intermediate_geo_nodes=[Wgs84GeoNode(33, 5), Wgs84GeoNode(37, 5)]
        )
        edge_8 = Edge(node_8, node_7)
        edge_9 = Edge(node_8, node_9)
        edge_10 = Edge(node_8, node_10)
        topology.add_nodes(
            [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_10]
        )
        topology.add_edges(
            [edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7, edge_8, edge_9, edge_10]
        )

        topology_a, topology_b, _ = Split.split(
            topology,
            split_edges={edge_3: 5.0, edge_5: 5.0, edge_6: 5.0, edge_7: 5.0, edge_8: 5.0},
            node_label_assignments={node_1: losn, node_6: losn, node_10: losn},
        )
        if losn == Label.A_Topology:
            assert [node_1, node_2, node_3, node_6, node_8, node_9, node_10] in topology_a
            assert [node_4, node_5, node_7] in topology_b
        else:
            assert [node_1, node_2, node_3, node_6, node_8, node_9, node_10] in topology_b
            assert [node_4, node_5, node_7] in topology_a


def test_split_without_split_edges_not_connected_topology():
    topology = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()
    node_a4 = Node()

    node_b1 = Node()
    node_b2 = Node()
    node_b3 = Node()
    node_b4 = Node()

    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)

    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)

    topology.add_nodes([node_a1, node_a2, node_a3, node_a4, node_b1, node_b2, node_b3, node_b4])
    topology.add_edges([edge_a1, edge_a2, edge_a3, edge_b1, edge_b2, edge_b3])

    topology_a, topology_b, _ = Split.split(
        topology,
        node_label_assignments={node_a1: Label.A_Topology, node_b1: Label.B_Topology},
    )

    assert [node_a1, node_a2, node_a3, node_a4, edge_a1, edge_a2, edge_a3] in topology_a
    assert [node_b1, node_b2, node_b3, node_b4, edge_b1, edge_b2, edge_b3] in topology_b


def test_split_without_split_edges_connected_topology():
    topology = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()
    node_a4 = Node()

    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)

    topology.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology.add_edges([edge_a1, edge_a2, edge_a3])

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            node_label_assignments={node_a1: Label.A_Topology, node_a4: Label.B_Topology},
        )

def test_topology_with_two_color_problem():
    topology = Topology()
    node_1 = Node(geo_node=DbrefGeoNode(x=0, y=0))
    node_3 = Node(geo_node=DbrefGeoNode(x=10, y=0))
    node_4 = Node(geo_node=DbrefGeoNode(x=30, y=0))
    node_5 = Node(geo_node=DbrefGeoNode(x=40, y=0))
    node_6 = Node(geo_node=DbrefGeoNode(x=20, y=5))
    node_7 = Node(geo_node=DbrefGeoNode(x=30, y=10))

    edge_1 = Edge(node_1, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_3, node_6, intermediate_geo_nodes=[DbrefGeoNode(x=12.5, y=5)])
    edge_5 = Edge(node_6, node_7, intermediate_geo_nodes=[DbrefGeoNode(x=22.5, y=10)])
    edge_6 = Edge(node_6, node_4, intermediate_geo_nodes=[DbrefGeoNode(x=27.5, y=5)])
    edge_7 = Edge(node_4, node_5)

    topology.add_nodes([node_1, node_3, node_4, node_5, node_6, node_7])
    topology.add_edges([edge_1, edge_3, edge_4, edge_5, edge_6, edge_7])

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            split_edges={edge_3: 5.0, edge_4: 5.0, edge_6: 5.0}
        )

def test_topology_with_two_color_problem_but_solvable():
    topology = Topology()

    node_6 = Node(geo_node=DbrefGeoNode(0, 5))
    node_7 = Node(geo_node=DbrefGeoNode(12.5, 5))  # Point
    node_8 = Node(geo_node=DbrefGeoNode(17.5, 5))  # Point
    node_9 = Node(geo_node=DbrefGeoNode(40, 5))

    node_1 = Node(geo_node=DbrefGeoNode(0, 0))
    node_2 = Node(geo_node=DbrefGeoNode(10, 0))  # Point
    node_3 = Node(geo_node=DbrefGeoNode(20, 0))  # Point
    node_4 = Node(geo_node=DbrefGeoNode(30, 0))  # Point
    node_5 = Node(geo_node=DbrefGeoNode(40, 0))

    node_A = Node(geo_node=DbrefGeoNode(20, -5))

    edge_1 = Edge(node_1, node_2)
    edge_2 = Edge(node_3, node_2)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_4, node_5)

    edge_5 = Edge(node_6, node_7)
    edge_6 = Edge(node_7, node_8)
    edge_7 = Edge(node_8, node_9)

    edge_9 = Edge(node_2, node_7)
    edge_10 = Edge(node_8, node_3)
    edge_11 = Edge(node_4, node_A, intermediate_geo_nodes=[DbrefGeoNode(27.5, -5)])

    topology.add_nodes(
        [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_A]
    )
    topology.add_edges(
        [edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7, edge_9, edge_10, edge_11]
    )

    topology_a, topology_b, _ = Split.split(topology,
                                            split_edges={edge_2: 5.0, edge_3: 5.0, edge_10: 2.795},
                                            node_label_assignments={node_4: Label.A_Topology}
                                            )
    assert [node_4, node_1] in topology_a
    assert [node_3] in topology_b

def test_validate_input():
    topology = Topology()
    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            split_edges={Edge(Node(), Node()): 5.0}
        )

    node_1 = Node(geo_node=DbrefGeoNode(x=0, y=0))
    node_3 = Node(geo_node=DbrefGeoNode(x=10, y=0))
    node_4 = Node(geo_node=DbrefGeoNode(x=30, y=0))
    node_5 = Node(geo_node=DbrefGeoNode(x=40, y=0))
    node_6 = Node(geo_node=DbrefGeoNode(x=20, y=5))
    node_7 = Node(geo_node=DbrefGeoNode(x=30, y=10))

    edge_1 = Edge(node_1, node_3)
    edge_3 = Edge(node_3, node_4)
    edge_4 = Edge(node_3, node_6, intermediate_geo_nodes=[DbrefGeoNode(x=12.5, y=5)])
    edge_5 = Edge(node_6, node_7, intermediate_geo_nodes=[DbrefGeoNode(x=22.5, y=10)])
    edge_6 = Edge(node_6, node_4, intermediate_geo_nodes=[DbrefGeoNode(x=27.5, y=5)])
    edge_7 = Edge(node_4, node_5)

    topology.add_nodes([node_1, node_3, node_4, node_5, node_6, node_7])
    topology.add_edges([edge_1, edge_3, edge_4, edge_5, edge_6, edge_7])

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            split_edges={Edge(Node(), Node()): 5.0}
        )

    with pytest.raises(ValueError):
        topology_a, topology_b, _ = Split.split(
            topology,
            node_label_assignments={Node(): Label.A_Topology}
        )