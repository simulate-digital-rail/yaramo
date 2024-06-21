from yaramo.model import Topology, Node, Edge

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