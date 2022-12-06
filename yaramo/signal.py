
from enum import Enum
from uuid import uuid4
from yaramo.base_element import BaseElement
from yaramo.edge import Edge

# Richtung
# IN
# GEGEN


class SignalDirection(Enum):
    IN = 1
    GEGEN = 2


class SignalFunction(Enum):
    Einfahr_Signal = 0
    Ausfahr_Signal = 1
    Blocksignal = 2
    andere = 3


class SignalKind(Enum):
    Hauptsignal = 0
    Mehrabschnittssignal = 1
    Vorsignal = 2
    Sperrsignal = 3
    Hauptsperrsignal = 4
    andere = 5


class Signal(BaseElement):

    def __init__(self, edge: Edge, distance_previous_node: float, direction: SignalDirection | str, function: SignalFunction | str, kind: SignalKind | str, side_distance: float = None,  **kwargs):
        super().__init__(**kwargs)
        self.trip = None
        self.edge = edge
        self.direction = SignalDirection.IN if direction == SignalDirection.IN or direction.lower() == SignalDirection.IN.name.lower() else SignalDirection.GEGEN
        self.side_distance: float = side_distance or 3.950 if self.direction == SignalDirection.IN else -3.950
        self.distance_previous_node = distance_previous_node
        self.classification_number = "60"
        self.control_member_uuid = str(uuid4())

        if isinstance(function, str):
            self.function = SignalFunction.__members__.get(function.lower(), SignalFunction.andere)
        elif isinstance(function, SignalFunction):
            self.function = function

        if isinstance(kind, str):
            self.kind = SignalKind.__members__.get(kind.lower(), SignalKind.andere)
        elif isinstance(kind, SignalKind):
            self.kind = kind

    def previous_node(self):
        return self.edge.node_a if self.direction == SignalDirection.IN else self.edge.node_b

    def next_node(self):
        return self.edge.node_b if self.direction == SignalDirection.IN else self.edge.node_a
