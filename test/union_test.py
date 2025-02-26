from yaramo.model import Topology, Node, Edge
from yaramo.operations import Union
import pytest


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

    assert len(topology_ab.nodes) == (len(topology_a.nodes) + len(topology_b.nodes) - 2)  # Minus Union Nodes
    assert len(topology_ab.edges) == (len(topology_a.edges) + len(topology_b.edges) - 2 + 1)  # Minus Union Edges + 1 new Edge
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

    assert len(topology_ab.nodes) == (len(topology_a.nodes) + len(topology_b.nodes) - 4)  # Minus Union Nodes
    assert len(topology_ab.edges) == (len(topology_a.edges) + len(topology_b.edges) - 4 + 2)  # Minus Union Edges + 2 new Edges
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

