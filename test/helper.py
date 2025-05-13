from yaramo.model import Edge, EuclideanGeoNode, Node


def create_geo_node(x, y):
    return EuclideanGeoNode(x, y)


def create_node(x, y):
    return Node(geo_node=create_geo_node(x, y))


def create_edge(node_a, node_b, inter_geo_nodes=None):
    return Edge(node_a, node_b, intermediate_geo_nodes=inter_geo_nodes)
