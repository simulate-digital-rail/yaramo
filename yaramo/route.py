from typing import Dict
from yaramo.base_element import BaseElement
from yaramo.model import Edge, Signal, SignalDirection
from typing import Optional

from yaramo.node import Node


class Route(BaseElement):

    def __init__(self, start_signal: Signal, maximum_speed: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.maximum_speed: int = maximum_speed
        self.edges: set[Edge] = set([start_signal.edge])
        self.start_signal: Signal = start_signal
        self.end_signal: Optional[Signal] = None

        self.edges.add(start_signal.edge)

    def get_length(self):
        length_sum = 0.0
        for edge in self.edges:
            length_sum = length_sum + float(edge.length)
        return length_sum

    def get_edges_in_order(self):
        if self.end_signal is None:
            return None

        previous_edge = self.start_signal.edge
        next_node = self.start_signal.next_node()
        edges_in_order = [previous_edge]

        while previous_edge is not self.end_signal.edge:
            next_edge = None
            for edge in self.edges:
                if edge.is_node_connected(next_node) and \
                   not edge.is_node_connected(previous_edge.get_other_node(next_node)):
                    next_edge = edge

            edges_in_order.append(next_edge)
            next_node = next_edge.get_other_node(next_node)
            previous_edge = next_edge

        return edges_in_order
    
    def contains_edge(self, _edge: Edge):
        for edge in self.edges:
            if edge.uuid == _edge.uuid:
                return True
        return False

    def duplicate(self):
        new_obj = Route(self.start_signal)
        new_obj.edges = []
        for edge in self.edges:
            new_obj.edges.append(edge)
        new_obj.end_signal = self.end_signal
        return new_obj

    def update_maximum_speed(self):
        edges = self.get_edges_in_order()
        nodes: list[Node] = []

        previous_node = self.start_signal.next_node()
        nodes.append(None)
        nodes.append(previous_node)

        for edge in edges[1:]:
            next_node = edge.node_a if edge.node_b == previous_node else edge.node_b
            nodes.append(next_node)
            previous_node = next_node

        maximum_speed = min([edge.maximum_speed or float('inf') for edge in edges])

        # We have to look back and ahead, as we have to figure out which branch of the node we traverse
        for index, node in enumerate(nodes):
            previous_node = nodes[index-1] if index > 0 else None
            next_node = nodes[index+1] if index + 1 < len(nodes) else None
            node_speed = None
            if node is not None:
                node_speed = node.maximum_speed(previous_node, next_node) 
            if node_speed is not None and node_speed < maximum_speed:
                maximum_speed = node_speed
        
        self.maximum_speed = maximum_speed

    def to_serializable(self) -> Dict:
        attributes = self.__dict__
        references = {
            'maximum_speed':self.maximum_speed,
            'edges':[edge.uuid for edge in self.edges],
            'start_signal':self.start_signal.uuid,
            'end_signal':self.end_signal.uuid if self.end_signal else None,
        }

        return {**attributes, **references}, {}
