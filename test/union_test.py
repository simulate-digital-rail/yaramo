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
from yaramo.operations import Union


def test_union():
    topology_a = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()  # Point
    node_a4 = Node()  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node()
    node_b2 = Node()
    node_b3 = Node()  # Point
    node_b4 = Node()  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    topology_ab = Union.union(topology_a, topology_b, {node_a4: node_b4})

    assert len(topology_ab.nodes) == (
        len(topology_a.nodes) + len(topology_b.nodes) - 2
    )  # Minus Union Nodes
    assert len(topology_ab.edges) == (
        len(topology_a.edges) + len(topology_b.edges) - 2 + 1
    )  # Minus Union Edges + 1 new Edge
    assert node_a3.is_point()
    assert node_b3.is_point()
    assert node_a1.uuid in topology_ab.nodes.keys()
    assert node_a2.uuid in topology_ab.nodes.keys()
    assert node_a3.uuid in topology_ab.nodes.keys()
    assert node_a4.uuid not in topology_ab.nodes.keys()
    assert node_b1.uuid in topology_ab.nodes.keys()
    assert node_b2.uuid in topology_ab.nodes.keys()
    assert node_b3.uuid in topology_ab.nodes.keys()
    assert node_b4.uuid not in topology_ab.nodes.keys()


def test_complex_union():
    topology_a = Topology()
    node_a1 = Node()
    node_a2 = Node()  # Point
    node_a3 = Node()  # Union-Node
    node_a4 = Node()  # Union-Node
    node_a5 = Node()  # Point
    node_a6 = Node()
    edge_a1 = Edge(node_a1, node_a2)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a2, node_a5)
    edge_a4 = Edge(node_a4, node_a5)
    edge_a5 = Edge(node_a5, node_a6)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4, node_a5, node_a6])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3, edge_a4, edge_a5])

    topology_b = Topology()
    node_b1 = Node()  # Union-Node
    node_b2 = Node()
    node_b3 = Node()  # Point
    node_b4 = Node()  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    topology_ab = Union.union(topology_a, topology_b, {node_a3: node_b1, node_a4: node_b4})

    assert len(topology_ab.nodes) == (
        len(topology_a.nodes) + len(topology_b.nodes) - 4
    )  # Minus Union Nodes
    assert len(topology_ab.edges) == (
        len(topology_a.edges) + len(topology_b.edges) - 4 + 2
    )  # Minus Union Edges + 2 new Edges
    assert node_a2.is_point()
    assert node_a5.is_point()
    assert node_b3.is_point()
    assert node_a1.uuid in topology_ab.nodes.keys()
    assert node_a2.uuid in topology_ab.nodes.keys()
    assert node_a3.uuid not in topology_ab.nodes.keys()
    assert node_a4.uuid not in topology_ab.nodes.keys()
    assert node_a5.uuid in topology_ab.nodes.keys()
    assert node_a6.uuid in topology_ab.nodes.keys()
    assert node_b1.uuid not in topology_ab.nodes.keys()
    assert node_b2.uuid in topology_ab.nodes.keys()
    assert node_b3.uuid in topology_ab.nodes.keys()
    assert node_b4.uuid not in topology_ab.nodes.keys()


def test_invalid_node_matching():
    topology_a = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()  # Point
    node_a4 = Node()  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node()
    node_b2 = Node()
    node_b3 = Node()  # Point
    node_b4 = Node()  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        topology_ab = Union.union(topology_a, topology_b, {node_b1: node_b4})


def test_point_as_node_matching():
    topology_a = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()  # Point
    node_a4 = Node()  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node()
    node_b2 = Node()
    node_b3 = Node()  # Point
    node_b4 = Node()  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    with pytest.raises(ValueError):
        topology_ab = Union.union(topology_a, topology_b, {node_a3: node_b4})


def test_other_objects_survive():
    topology_a = Topology()
    node_a1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_a2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_a3 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_a4 = Node(geo_node=Wgs84GeoNode(30, 0))  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a3, node_a4)
    signal_a1 = Signal(
        edge=edge_a1,
        distance_edge=5.0,
        direction=SignalDirection.IN,
        function=SignalFunction.Einfahr_Signal,
        kind=SignalKind.Hauptsignal,
    )
    signal_a2 = Signal(
        edge=edge_a3,
        distance_edge=5.0,
        direction=SignalDirection.IN,
        function=SignalFunction.Ausfahr_Signal,
        kind=SignalKind.Hauptsignal,
    )  # On Union-Edge
    route_a1 = Route(signal_a1)
    route_a1.edges = {edge_a1, edge_a3}
    route_a1.end_signal = signal_a2
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])
    topology_a.add_signals([signal_a1, signal_a2])
    topology_a.add_routes([route_a1])

    topology_b = Topology()
    node_b1 = Node(geo_node=Wgs84GeoNode(60, 0))
    node_b2 = Node(geo_node=Wgs84GeoNode(60, 10))
    node_b3 = Node(geo_node=Wgs84GeoNode(50, 0))  # Point
    node_b4 = Node(geo_node=Wgs84GeoNode(40, 0))  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    signal_b1 = Signal(
        edge=edge_b1,
        distance_edge=4.0,
        direction=SignalDirection.IN,
        function=SignalFunction.Einfahr_Signal,
        kind=SignalKind.Hauptsignal,
    )
    signal_b2 = Signal(
        edge=edge_b3,
        distance_edge=4.0,
        direction=SignalDirection.IN,
        function=SignalFunction.Ausfahr_Signal,
        kind=SignalKind.Hauptsignal,
    )  # On Union-Edge
    route_b1 = Route(signal_b1)
    route_b1.edges = {edge_b1, edge_b3}
    route_b1.end_signal = signal_b2
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])
    topology_b.add_signals([signal_b1, signal_b2])
    topology_b.add_routes([route_b1])

    topology_ab = Union.union(topology_a, topology_b, {node_a4: node_b4})
    assert len(topology_ab.signals) == 4
    assert len(topology_ab.routes) == 2


def test_transitive_union_test():
    topology_a = Topology()
    node_a1 = Node()
    node_a2 = Node()
    node_a3 = Node()  # Point
    node_a4 = Node()  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a4, node_a3)
    topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
    topology_a.add_edges([edge_a1, edge_a2, edge_a3])

    topology_b = Topology()
    node_b1 = Node()  # Union-Node
    node_b2 = Node()
    node_b3 = Node()  # Point
    node_b4 = Node()  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b4, node_b3)
    topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
    topology_b.add_edges([edge_b1, edge_b2, edge_b3])

    topology_ab = Union.union(topology_a, topology_b, {node_a4: node_b4})

    topology_c = Topology()
    node_c1 = Node()  # Union-Node
    node_c2 = Node()
    edge_c1 = Edge(node_c1, node_c2)
    topology_c.add_nodes([node_c1, node_c2])
    topology_c.add_edges([edge_c1])

    topology_abc = Union.union(topology_ab, topology_c, {node_b1: node_c1})

    assert len(topology_abc.nodes) == (
        len(topology_ab.nodes) + len(topology_c.nodes) - 2
    )  # Minus Union Nodes
    assert len(topology_abc.edges) == (
        len(topology_ab.edges) + len(topology_c.edges) - 2 + 1
    )  # Minus Union Edges + 1 new Edge
