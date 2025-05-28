import itertools

from yaramo.model import Edge, Node, Track, TrackType


def test_edges_in_order():
    node_a = Node()
    node_b = Node()
    node_c = Node()
    node_d = Node()
    edge_a = Edge(node_a, node_b)
    edge_b = Edge(node_b, node_c)
    edge_c = Edge(node_c, node_d)
    track = Track(TrackType.Hauptgleis)
    edge_list = [edge_a, edge_b, edge_c]
    for permutation in list(itertools.permutations(edge_list)):
        track.add_edge_section(permutation[0], 0.0, 5.0)
        track.add_edge_section(permutation[1], 0.0, 5.0)
        track.add_edge_section(permutation[2], 0.0, 5.0)
        assert track.get_edges_in_order() == edge_list
