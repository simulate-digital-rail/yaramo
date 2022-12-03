from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode
from yaramo.node import Node


class Edge(BaseElement):

    def __init__(self, node_a: Node, node_b: Node, length: float=None, **kwargs):
        super().__init__(**kwargs)
        self.node_a = node_a
        self.node_b = node_b
        self.intermediate_geo_nodes: list[GeoNode] = []
        self.signals = []
        self.length = length

    def is_node_connected(self, other_node):
        return self.node_a == other_node or self.node_b == other_node

    def get_other_node(self, node):
        if self.node_a == node:
            return self.node_b
        return self.node_a

    def update_length(self):
        self.length = self.__get_length()
    
    def __get_length(self) -> float:
        if len(self.intermediate_geo_nodes) == 0:
            return self.node_a.geo_node.get_distance_to_other_geo_node(self.node_b.geo_node)

        total_length = self.node_a.geo_node.get_distance_to_other_geo_node(self.intermediate_geo_nodes[0])

        for i in range(len(self.intermediate_geo_nodes) - 1):
            geo_node_a = self.intermediate_geo_nodes[i]
            geo_node_b = self.intermediate_geo_nodes[i + 1]
            total_length += geo_node_a.get_distance_to_other_geo_node(geo_node_b)

        total_length += self.intermediate_geo_nodes[-1].get_distance_to_other_geo_node(self.node_b.geo_node)
        return total_length
