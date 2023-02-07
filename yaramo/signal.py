from enum import Enum
from typing import Tuple, List, Set
from uuid import uuid4

from yaramo.additional_signal import AdditionalSignal
from yaramo.base_element import BaseElement
from yaramo.edge import Edge
from yaramo.trip import Trip


class SignalDirection(Enum):
    IN = 1
    GEGEN = 2

    def __str__(self):
        return self.name.lower()


class SignalFunction(Enum):
    Einfahr_Signal = 0
    Ausfahr_Signal = 1
    Block_Signal = 2
    andere = 3

    def __str__(self):
        return self.name


class SignalKind(Enum):
    Hauptsignal = 0
    Mehrabschnittssignal = 1
    Vorsignal = 2
    Sperrsignal = 3
    Hauptsperrsignal = 4
    andere = 5

    def __str__(self):
        return self.name


class SignalState(Enum):
    hp0 = 0
    hp1 = 1
    hp2 = 2
    ks1 = 3
    ks2 = 4
    sh1 = 5
    sh2 = 6


class Signal(BaseElement):
    def __init__(
        self,
        edge: Edge,
        distance_edge: float,
        direction: SignalDirection | str,
        function: SignalFunction | str,
        kind: SignalKind | str,
        side_distance: float = None,
        supported_states: Set[SignalState] = None,
        classification_number: int = 60,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.trip: Trip = None
        self.edge = edge
        self.distance_edge = distance_edge  # distance to edge.node_a in meters
        self.classification_number = classification_number
        self.control_member_uuid = str(uuid4())
        self.additional_signals: list[AdditionalSignal] = []
        self.supported_states: Set[SignalState] = supported_states if supported_states else set()

        if isinstance(direction, str):
            self.direction = SignalDirection.GEGEN if direction == "gegen" else SignalDirection.IN
        elif isinstance(direction, SignalDirection):
            self.direction = direction

        if side_distance is not None:
            self.side_distance = (
                side_distance if self.direction == SignalDirection.IN else -side_distance
            )
        else:
            self.side_distance = 3.950 if self.direction == SignalDirection.IN else -3.950

        if isinstance(function, str):
            self.function = SignalFunction.__members__.get(function, SignalFunction.andere)
        elif isinstance(function, SignalFunction):
            self.function = function

        if isinstance(kind, str):
            self.kind = SignalKind.__members__.get(kind, SignalKind.andere)
        elif isinstance(kind, SignalKind):
            self.kind = kind

    def previous_node(self):
        return self.edge.node_a if self.direction == SignalDirection.IN else self.edge.node_b

    def next_node(self):
        return self.edge.node_b if self.direction == SignalDirection.IN else self.edge.node_a

    def to_serializable(self) -> Tuple[dict, dict]:
        attributes, _ = super().to_serializable()
        references = {
            "edge": self.edge.uuid if self.edge else None,
            "trip": self.trip.uuid if self.trip else None,
            "additional_signals": [signal.uuid for signal in self.additional_signals],
            "direction": str(self.direction),
            "side_distance": self.side_distance,
            "function": str(self.function),
            "kind": str(self.kind),
        }
        objects = {}
        items = [self.trip] + self.additional_signals if self.trip else self.additional_signals
        for item in items:
            item_object, serialized_item = item.to_serializable()
            objects = {**objects, item.uuid: item_object, **serialized_item}

        return {**attributes, **references}, objects
