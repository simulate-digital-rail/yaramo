from helper import create_edge, create_geo_node, create_node

from yaramo.model import Edge, Node, Topology


def test_get_edge_by_nodes():
    topology = Topology()

    node_a = Node()
    node_b = Node()
    node_c = Node()
    topology.add_node(node_a)
    topology.add_node(node_b)
    topology.add_node(node_c)
    assert len(topology.nodes) == 3

    edge = Edge(node_a, node_b)
    topology.add_edge(edge)
    assert len(topology.edges) == 1

    def _test_edge(_node_a, _node_b, _expected_edge):
        _edge = topology.get_edge_by_nodes(_node_a, _node_b)
        assert _edge == _expected_edge

    _test_edge(node_a, node_b, edge)
    _test_edge(node_b, node_a, edge)
    _test_edge(node_a, node_c, None)


def test_json_export_and_import():
    topology = Topology()

    node_a = Node()
    node_b = Node()
    topology.add_node(node_a)
    topology.add_node(node_b)
    edge = Edge(node_a, node_b)
    topology.add_edge(edge)

    json_str = topology.to_json()
    topology_copy = Topology.from_json(json_str)

    assert len(topology.nodes) == len(topology_copy.nodes)
    assert len(topology.edges) == len(topology_copy.edges)
    assert len(topology.signals) == len(topology_copy.signals)
    assert len(topology.routes) == len(topology_copy.routes)


def test_station_topology():
    """
    This test creates this kind of topology:
         ______
    ____/______\\____
    This kind wouldn't be possible in yaramo 1, since
    two edges connect the same points.
    """
    end_a = create_node(0, 0)
    point_a = create_node(10, 0)
    inter_geo_node_a = create_geo_node(13, 1)
    inter_geo_node_b = create_geo_node(17, 1)
    point_b = create_node(20, 0)
    end_b = create_node(30, 0)

    edge_1 = create_edge(end_a, point_a)
    edge_2a = create_edge(point_a, point_b)
    edge_2b = create_edge(point_a, point_b, inter_geo_nodes=[inter_geo_node_a, inter_geo_node_b])
    edge_3 = create_edge(point_b, end_b)

    end_a.calc_anschluss_of_all_edges()
    point_a.calc_anschluss_of_all_edges()
    point_b.calc_anschluss_of_all_edges()
    end_b.calc_anschluss_of_all_edges()

    assert len(end_a.connected_edges) == 1
    assert end_a.connected_edge_on_head == edge_1
    assert len(point_a.connected_edges) == 3
    assert point_a.connected_edge_on_head == edge_1
    assert point_a.connected_edge_on_left == edge_2b
    assert point_a.connected_edge_on_right == edge_2a
    assert len(point_b.connected_edges) == 3
    assert point_b.connected_edge_on_head == edge_3
    assert point_b.connected_edge_on_right == edge_2b
    assert point_b.connected_edge_on_left == edge_2a
    assert len(end_b.connected_edges) == 1
    assert end_b.connected_edge_on_head == edge_3
