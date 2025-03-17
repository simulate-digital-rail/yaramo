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

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

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

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

    assert (
        len(topology_a.nodes) == len([node_1, node_2, node_3, node_4]) + 2
    )  # Plus two new track ends
    assert (
        len(topology_b.nodes) == len([node_5, node_6, node_7, node_8]) + 2
    )  # Plus two new track ends
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
        topology_a, topology_b = Split.split(topology, split_edges={edge_3: 20.0})


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
        topology_a, topology_b = Split.split(topology, split_edges={edge_3: 5.0})


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
        topology_a, topology_b = Split.split(topology, split_edges={edge_4: 5.0})


def test_invalid_split_more_than_two_partitions():
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

    with pytest.raises(ValueError):
        topology_a, topology_b = Split.split(topology, split_edges={edge_3: 5.0, edge_5: 5.0})


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

    topology_a, topology_b = Split.split(topology, split_edges={edge_3: 7.0})

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

    assert len(topology_a.signals) == 2
    assert signal_1.uuid in topology_a.signals.keys()
    assert signal_2.uuid in topology_a.signals.keys()
    assert len(topology_b.signals) == 1
    assert signal_3.uuid in topology_b.signals.keys()


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
    topology_a, topology_b = Split.split(topology, split_edges={edge_3: 5.0})

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

    topology_b, topology_c = Split.split(topology_b, split_edges={edge_5: 10.0})

    assert node_4.uuid in topology_b.nodes or node_4.uuid in topology_c.nodes
    if node_4.uuid in topology_c.nodes:
        topology_b, topology_c = topology_c, topology_b

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

    def _check_list_in_list(_source_list, _expected_in_list):
        assert all(_item.uuid in _source_list.keys() for _item in _expected_in_list)

    _check_list_in_list(topology_a.nodes, expected_nodes_in_a)
    _check_list_in_list(topology_a.edges, expected_edges_in_a)
    _check_list_in_list(topology_b.nodes, expected_nodes_in_b)
    _check_list_in_list(topology_b.edges, expected_edges_in_b)
    _check_list_in_list(topology_c.nodes, expected_nodes_in_c)
    _check_list_in_list(topology_c.edges, expected_edges_in_c)


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

    topology_a, topology_b = Split.split(topology, split_edges={edge_3: 32.0})

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

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

    topology_a, topology_b = Split.split(topology, split_edges={edge_3: 5.0})

    assert node_1.uuid in topology_a.nodes or node_1.uuid in topology_b.nodes
    if node_1.uuid in topology_b.nodes:
        topology_a, topology_b = topology_b, topology_a

    # Note: route 3 goes over split edge, so it gets removed
    assert len(topology_a.routes) == 1
    assert route_1 in topology_a.routes.values()
    assert len(topology_a.signals) == 3
    assert len(topology_b.routes) == 1
    assert route_2 in topology_b.routes.values()
    assert len(topology_b.signals) == 3
