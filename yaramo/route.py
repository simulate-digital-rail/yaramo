from yaramo.base_element import BaseElement
from yaramo.edge import Edge
from yaramo.signal import Signal


class Route(BaseElement):

    def __init__(self, maximum_speed, start_signal: Signal, **kwargs):
        super().__init__(**kwargs)
        self.maximum_speed: int = maximum_speed
        self.edges: set[Edge] = set()
        self.start_signal: Signal = start_signal
        self.end_signal: Signal = None

        self.edges.add(start_signal.edge)

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
