from typing import Dict
from yaramo.base_element import BaseElement
from yaramo.model import Edge, Signal
from typing import Optional


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

    def to_serializable(self) -> Dict:
        output_dict = dict()
        output_dict["start_signal"] = self.start_signal.uuid
        output_dict["edges"] = []

        for i in range(0, len(self.edges)):
            edge = self.edges[i]
            from_d = 0.0
            to_d = 0.0

            if i == 0:
                if self.start_signal.direction == SignalDirection.IN:
                    from_d = self.start_signal.distance_previous_node
                    to_d = edge.length
                else:
                    from_d = self.start_signal.distance_previous_node
                    to_d = 0.0
                output_dict["edges"].append({"edge_uuid": edge.uuid, "from": float(from_d), "to": float(to_d)})
            elif i == len(self.edges) - 1:
                if self.end_signal.direction == SignalDirection.IN:
                    from_d = 0.0
                    to_d = self.end_signal.distance_previous_node
                else:
                    from_d = edge.length
                    to_d = self.end_signal.distance_previous_node
                output_dict["edges"].append({"edge_uuid": edge.uuid, "from": float(from_d), "to": float(to_d)})
                pass
            else:
                output_dict["edges"].append({"edge_uuid": edge.uuid, "from": float(0), "to": float(edge.length)})

        output_dict["end_signal"] = self.end_signal.uuid
        return output_dict
