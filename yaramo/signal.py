
from uuid import uuid4
from yaramo.base_element import BaseElement
from yaramo.edge import Edge


class Signal(BaseElement):

    def __init__(self, edge: Edge, distance_previous_node: float, direction: str, function: str, kind: str, side_distance: float = None,  **kwargs):
        super().__init__(**kwargs)
        self.trip = None
        self.edge = edge
        self.side_distance: float = side_distance
        self.distance_previous_node = distance_previous_node
        self.direction = direction.lower()
        self.classification_number = "60"
        self.control_member_uuid = str(uuid4())

        if function in Signal.get_supported_functions():
            self.function = function
        else:
            self.function = Signal.get_supported_functions()[0]

        if kind in Signal.get_supported_kinds():
            self.kind = kind
        else:
            self.kind = Signal.get_supported_kinds()[0]


    def previous_node(self):
        return self.edge.node_a if self.direction == "in" else self.edge.node_b

    def next_node(self):
        return self.edge.node_b if self.direction == "in" else self.edge.node_a

    @staticmethod
    def get_supported_functions():
        return ["Einfahr_Signal", "Ausfahr_Signal", "Blocksignal", "andere"]

    @staticmethod
    def get_supported_kinds():
        return ["Hauptsignal", "Mehrabschnittssignal", "Vorsignal", "Sperrsignal", "Hauptsperrsignal", "andere"]
