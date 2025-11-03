from typing import List

import pytest

from yaramo.model import (
    Edge,
    EuclideanGeoNode,
    Node,
    Route,
    Signal,
    SignalDirection,
    SignalFunction,
    SignalKind,
    Topology,
    Track,
    TrackType,
    Wgs84GeoNode,
)
from yaramo.operations import Union


def test_simple_union():
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

    topology_ab = Union.union(topology_a, {node_a4: node_b4}, topology_b)

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

    topology_ab = Union.union(topology_a, {node_a3: node_b1, node_a4: node_b4}, topology_b)

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
        topology_ab = Union.union(topology_a, {node_b1: node_b4}, topology_b)


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
        topology_ab = Union.union(topology_a, {node_a3: node_b4}, topology_b)


def test_other_objects_survive():
    topology_a = Topology()
    node_a1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_a2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_a3 = Node(geo_node=Wgs84GeoNode(20, 0))  # Point
    node_a4 = Node(geo_node=Wgs84GeoNode(30, 0))  # Union-Node
    edge_a1 = Edge(node_a1, node_a3)
    edge_a2 = Edge(node_a2, node_a3)
    edge_a3 = Edge(node_a3, node_a4)
    track_a = Track(TrackType.sonstige)
    track_a.add_edge_section(edge_a1, 0.0, 5.0)
    track_a.add_edge_section(edge_a2, 0.0, 5.0)
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
    topology_a.add_tracks([track_a])

    topology_b = Topology()
    node_b1 = Node(geo_node=Wgs84GeoNode(60, 0))
    node_b2 = Node(geo_node=Wgs84GeoNode(60, 10))
    node_b3 = Node(geo_node=Wgs84GeoNode(50, 0))  # Point
    node_b4 = Node(geo_node=Wgs84GeoNode(40, 0))  # Union-Node
    edge_b1 = Edge(node_b1, node_b3)
    edge_b2 = Edge(node_b2, node_b3)
    edge_b3 = Edge(node_b3, node_b4)
    track_b = Track(TrackType.sonstige)
    track_b.add_edge_section(edge_b2, 0.0, 5.0)
    track_b.add_edge_section(edge_b3, 0.0, 5.0)
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
    topology_b.add_tracks([track_b])

    topology_ab = Union.union(topology_a, {node_a4: node_b4}, topology_b)
    assert len(topology_ab.signals) == 4
    assert len(topology_ab.routes) == 2
    assert len(topology_ab.tracks) == 2


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

    topology_ab = Union.union(topology_a, {node_a4: node_b4}, topology_b)

    topology_c = Topology()
    node_c1 = Node()  # Union-Node
    node_c2 = Node()
    edge_c1 = Edge(node_c1, node_c2)
    topology_c.add_nodes([node_c1, node_c2])
    topology_c.add_edges([edge_c1])

    topology_abc = Union.union(topology_ab, {node_b1: node_c1}, topology_c)

    assert len(topology_abc.nodes) == (
        len(topology_ab.nodes) + len(topology_c.nodes) - 2
    )  # Minus Union Nodes
    assert len(topology_abc.edges) == (
        len(topology_ab.edges) + len(topology_c.edges) - 2 + 1
    )  # Minus Union Edges + 1 new Edge


def test_geo_node_union():
    topology_a = Topology()
    node_1 = Node(geo_node=Wgs84GeoNode(0, 0))
    node_2 = Node(geo_node=Wgs84GeoNode(0, 10))
    node_3 = Node(geo_node=Wgs84GeoNode(10, 0))  # Point
    node_3_end = Node(geo_node=Wgs84GeoNode(22, 10))
    edge_1 = Edge(node_1, node_3)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(node_3, node_3_end)
    edge_3.intermediate_geo_nodes.extend([Wgs84GeoNode(16, 3)])
    topology_a.add_nodes([node_1, node_2, node_3, node_3_end])
    topology_a.add_edges([edge_1, edge_2, edge_3])

    topology_b = Topology()
    node_4_end = Node(geo_node=Wgs84GeoNode(23, 11))  # Point
    node_4 = Node(geo_node=Wgs84GeoNode(30, 30))  # Point
    node_5 = Node(geo_node=Wgs84GeoNode(30, 40))
    node_6 = Node(geo_node=Wgs84GeoNode(40, 40))
    edge_4 = Edge(node_4, node_4_end)
    edge_4.intermediate_geo_nodes.extend([Wgs84GeoNode(27, 24), Wgs84GeoNode(28, 25)])
    edge_5 = Edge(node_4, node_5)
    edge_6 = Edge(node_4, node_6)
    topology_b.add_nodes([node_4_end, node_4, node_5, node_6])
    topology_b.add_edges([edge_4, edge_5, edge_6])

    topology_ab = Union.union(topology_a, {node_3_end: node_4_end}, topology_b)

    def _count_geo_node(_topology: Topology):
        return sum(map(lambda _edge: len(_edge.intermediate_geo_nodes), _topology.edges.values()))

    assert _count_geo_node(topology_a) == 1
    assert _count_geo_node(topology_b) == 2
    assert _count_geo_node(topology_ab) == 5  # 3 from previous + 2 union nodes


def test_corner_cases_edge_directions():
    configs = [
        {
            "switch_edge_a3": False,
            "switch_edge_b3": False,
            "signal_a1_distance": 4.0,
            "signal_b1_distance": 21.0,
            "signal_a1_direction": SignalDirection.IN,
            "signal_b1_direction": SignalDirection.GEGEN,
        },
        {
            "switch_edge_a3": False,
            "switch_edge_b3": True,
            "signal_a1_distance": 4.0,
            "signal_b1_distance": 19.0,
            "signal_a1_direction": SignalDirection.IN,
            "signal_b1_direction": SignalDirection.IN,
        },
        {
            "switch_edge_a3": True,
            "switch_edge_b3": False,
            "signal_a1_distance": 6.0,
            "signal_b1_distance": 21.0,
            "signal_a1_direction": SignalDirection.GEGEN,
            "signal_b1_direction": SignalDirection.GEGEN,
        },
        {
            "switch_edge_a3": True,
            "switch_edge_b3": True,
            "signal_a1_distance": 6.0,
            "signal_b1_distance": 19.0,
            "signal_a1_direction": SignalDirection.GEGEN,
            "signal_b1_direction": SignalDirection.IN,
        },
    ]

    def _are_geo_nodes_in_ascending_order(_geo_node_list: List[EuclideanGeoNode]):
        current_x = _geo_node_list[0].x
        print(current_x)
        for geo_node in _geo_node_list:
            print(geo_node.x)
            if geo_node.x < current_x:
                return False
            current_x = geo_node.x
        return True

    for config in configs:
        print(config)
        topology_a = Topology()
        node_a1 = Node(geo_node=EuclideanGeoNode(0, 0))
        node_a2 = Node(geo_node=EuclideanGeoNode(0, 10))
        node_a3 = Node(geo_node=EuclideanGeoNode(10, 0))  # Point
        node_a4 = Node(geo_node=EuclideanGeoNode(20, 0))  # Union-Node
        edge_a1 = Edge(node_a1, node_a3)
        edge_a2 = Edge(node_a2, node_a3)
        if config["switch_edge_a3"]:
            edge_a3 = Edge(node_a4, node_a3)
            edge_a3.intermediate_geo_nodes.extend(
                [EuclideanGeoNode(17, 0), EuclideanGeoNode(16, 0)]
            )
        else:
            edge_a3 = Edge(node_a3, node_a4)
            edge_a3.intermediate_geo_nodes.extend(
                [EuclideanGeoNode(16, 0), EuclideanGeoNode(17, 0)]
            )

        signal_a1 = Signal(
            edge=edge_a3,
            distance_edge=4.0,
            direction=SignalDirection.IN,
            function=SignalFunction.Block_Signal,
            kind=SignalKind.Hauptsignal,
        )
        edge_a3.signals.append(signal_a1)

        topology_a.add_nodes([node_a1, node_a2, node_a3, node_a4])
        topology_a.add_edges([edge_a1, edge_a2, edge_a3])
        topology_a.add_signals([signal_a1])

        edge_a3.update_length()
        assert edge_a3.length == 10.0

        topology_b = Topology()
        node_b1 = Node(geo_node=EuclideanGeoNode(45, 0))
        node_b2 = Node(geo_node=EuclideanGeoNode(45, 10))
        node_b3 = Node(geo_node=EuclideanGeoNode(35, 0))  # Point
        node_b4 = Node(geo_node=EuclideanGeoNode(25, 0))  # Union-Node
        edge_b1 = Edge(node_b1, node_b3)
        edge_b2 = Edge(node_b2, node_b3)
        if config["switch_edge_b3"]:
            edge_b3 = Edge(node_b3, node_b4)
            edge_b3.intermediate_geo_nodes.extend(
                [EuclideanGeoNode(32, 0), EuclideanGeoNode(31, 0)]
            )
        else:
            edge_b3 = Edge(node_b4, node_b3)
            edge_b3.intermediate_geo_nodes.extend(
                [EuclideanGeoNode(31, 0), EuclideanGeoNode(32, 0)]
            )

        signal_b1 = Signal(
            edge=edge_b3,
            distance_edge=4.0,
            direction=SignalDirection.IN,
            function=SignalFunction.Block_Signal,
            kind=SignalKind.Hauptsignal,
        )
        edge_b3.signals.append(signal_b1)

        topology_b.add_nodes([node_b1, node_b2, node_b3, node_b4])
        topology_b.add_edges([edge_b1, edge_b2, edge_b3])
        topology_a.add_signals([signal_b1])

        edge_b3.update_length()
        assert edge_b3.length == 10.0

        topology_ab = Union.union(topology_a, {node_a4: node_b4}, topology_b)

        assert signal_a1 in topology_ab.signals.values()
        assert signal_b1 in topology_ab.signals.values()
        union_edge: Edge = topology_ab.get_edge_by_nodes(node_a3, node_b3)[0]
        union_edge.update_length()
        assert union_edge.length == 25.0
        assert signal_a1 in union_edge.signals
        assert signal_b1 in union_edge.signals
        assert signal_a1.distance_edge == config["signal_a1_distance"]
        assert signal_b1.distance_edge == config["signal_b1_distance"]
        assert signal_a1.direction == config["signal_a1_direction"]
        assert signal_b1.direction == config["signal_b1_direction"]
        assert _are_geo_nodes_in_ascending_order(union_edge.intermediate_geo_nodes)


def test_union_in_one_topology():
    topology_a = Topology()
    node_1 = Node(geo_node=EuclideanGeoNode(0, 0))
    node_2 = Node(geo_node=EuclideanGeoNode(10, 0))
    node_3 = Node(geo_node=EuclideanGeoNode(14, 0))
    node_4 = Node(geo_node=EuclideanGeoNode(16, 0))
    node_5 = Node(geo_node=EuclideanGeoNode(20, 0))
    node_6 = Node(geo_node=EuclideanGeoNode(30, 0))
    edge_1 = Edge(node_1, node_2)
    edge_2 = Edge(node_2, node_3)
    edge_3 = Edge(
        node_2, node_5, intermediate_geo_nodes=[EuclideanGeoNode(13, 5), EuclideanGeoNode(17, 5)]
    )
    edge_4 = Edge(node_5, node_4)
    edge_5 = Edge(node_5, node_6)
    topology_a.add_nodes([node_1, node_2, node_3, node_4, node_5, node_6])
    topology_a.add_edges([edge_1, edge_2, edge_3, edge_4, edge_5])

    topology_ab = Union.union(topology_a, {node_3: node_4})
    assert [node_1, node_2, node_5, node_6] in topology_ab
    assert [node_3, node_4] not in topology_ab
    assert len(topology_ab.edges) == 4
