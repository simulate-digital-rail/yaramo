from typing import List
from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode
from yaramo.node import Node
from yaramo.signal import Signal, SignalDirection


class Edge(BaseElement):

    def __init__(self, node_a: Node, node_b: Node, length: float=None, **kwargs):
        super().__init__(**kwargs)
        self.node_a = node_a
        self.node_b = node_b
        self.intermediate_geo_nodes: list[GeoNode] = []
        self.signals: list[Signal] = []
        self.length = length

    def is_node_connected(self, other_node) -> bool:
        return self.node_a == other_node or self.node_b == other_node

    def get_other_node(self, node: Node) -> Node:
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
    
    def get_direction_based_on_nodes(self, node_a, node_b) -> SignalDirection:
        if self.node_a.uuid == node_a.uuid and self.node_b.uuid == node_b.uuid:
            return SignalDirection.IN
        elif self.node_a.uuid == node_b.uuid and self.node_b.uuid == node_a.uuid:
            return SignalDirection.GEGEN
        return None

    def get_signals_with_direction_in_order(self, direction) -> List[Signal]:
        result: list[Signal] = []
        for signal in self.signals:
            if signal.direction == direction:
                result.append(signal)
        result.sort(key=lambda x: x.distance_previous_node, reverse=(direction == SignalDirection.GEGEN))
        return result
