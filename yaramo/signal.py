from typing import Tuple
from yaramo.additional_signal import AdditionalSignal
from enum import Enum
from uuid import uuid4
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


class Signal(BaseElement):

    def __init__(self, edge: Edge, distance_edge: float, direction: SignalDirection | str, function: SignalFunction | str, kind: SignalKind | str, side_distance: float = None,  **kwargs):
        super().__init__(**kwargs)
        self.trip: Trip = None
        self.edge = edge
        self.distance_edge = distance_edge
        self.classification_number = "60"
        self.control_member_uuid = str(uuid4())
        self.additional_signals: list[AdditionalSignal] = []
        
        if isinstance(direction, str):
            self.direction = SignalDirection.GEGEN if direction == "gegen" else SignalDirection.IN
        elif isinstance(direction, SignalDirection):
            self.direction = direction

        if side_distance is not None:
            self.side_distance = side_distance if self.direction == SignalDirection.IN else -side_distance
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
    
    @property
    def distance_previous_node(self):
        if self.direction == SignalDirection.IN:
            return self.distance_edge
        else:
            return self.edge.length - self.distance_edge

    def to_serializable(self) -> Tuple[dict, dict]:
        base, _ = super().to_serializable()
        sub = {
            'trip': self.trip,
            'distance_edge': self.distance_edge,
            'classification_number': self.classification_number,
            'control_member_uuid': self.control_member_uuid,
            'edge': self.edge.uuid if self.edge else None,
            'trip':self.trip.uuid if self.trip else None,
            'additional_signals': [signal.uuid for signal in self.additional_signals],
            'direction': str(self.direction),
            'side_distance': self.side_distance,
            'function': str(self.function),
            'kind': str(self.kind),
        }
        trip_objects = {}
        if self.trip:
            trip, trip_object = self.trip.to_serializable()
            trip_objects = {self.trip.uuid:trip, **trip_object}
        signal_objects = {}
        for additional_signal in self.additional_signals:
            if additional_signal:
                signal, signal_object = additional_signal.to_serializable()
                signal_objects = {**signal_objects, **{additional_signal.uuid:signal, **signal_object}}
        return {**base, **sub}, {**signal_objects, **trip_objects}

