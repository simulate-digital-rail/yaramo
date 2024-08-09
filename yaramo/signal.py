from enum import Enum
from typing import Set, Tuple
from uuid import uuid4

from yaramo.additional_signal import AdditionalSignal
from yaramo.base_element import BaseElement
from yaramo.edge import Edge
from yaramo.trip import Trip


class SignalDirection(Enum):
    """The SignalDirection determines whether or not a Signal points in or against the direction of it's Edge."""

    IN = 1
    GEGEN = 2

    def __str__(self):
        return self.name.lower()


class SignalFunction(Enum):
    """The SignalFunction determines the function of a Signal."""

    Einfahr_Signal = 0
    Ausfahr_Signal = 1
    Block_Signal = 2
    andere = 3

    def __str__(self):
        return self.name


class SignalKind(Enum):
    """The SignalFunction determines the type of a Signal."""

    Hauptsignal = 0
    Mehrabschnittssignal = 1
    Vorsignal = 2
    Sperrsignal = 3
    Hauptsperrsignal = 4
    andere = 5

    def __str__(self):
        return self.name


class SignalState(Enum):
    """The SignalState determines a possible state of a Signal."""

    hp0 = 0
    hp1 = 1
    hp2 = 2
    ks1 = 3
    ks2 = 4
    sh1 = 5
    sh2 = 6


class Signal(BaseElement):
    """A Signal is a track element associated with an edge. It has an application direction and
    is characterized by it's function, kind, supported_states and associated additional_signals.
    A Signal can have a side distance determining the orthogonal distance to the actual track an Edge symbolises.
    """

    def __init__(
        self,
        edge: Edge,
        distance_edge: float,
        direction: SignalDirection | str,
        function: SignalFunction | str,
        kind: SignalKind | str,
        side_distance: float = None,
        supported_states: Set[SignalState] = None,
        classification_number: str = "60",
        **kwargs
    ):
        """
        Parameters
        ----------
        distance_edge : float
            The distance to edge.node_a in meters
        side_distance : float
            The orthogonal distance to the edge in meters (default is (-)3.950)
        classification_number : str
            The classification_number of the edge
        control_member_uuid : str
            The control_member_uuid of the edge
        additional_signals: list[AdditionalSignal]
            Additional_signals connected to that Signal
        supported_states: Set[SignalState]
            Different SignalStates a Signal can show
        """

        super().__init__(**kwargs)
        self.trip: Trip = None
        self.edge = edge
        self.distance_edge = distance_edge
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
        """Return the node connecting the Signal's edge which came before the Signal (with relative direction on the edge)."""
        return self.edge.node_a if self.direction == SignalDirection.IN else self.edge.node_b

    def next_node(self):
        """Return the node connecting the Signal's edge which comes after the Signal (with relative direction on the edge)."""
        return self.edge.node_b if self.direction == SignalDirection.IN else self.edge.node_a

    def to_serializable(self) -> Tuple[dict, dict]:
        """See the description in the BaseElement class.

        Returns:
            A serializable dictionary and a dictionary with serialized objects (AdditionalSignals and Trip).
        """

        attributes, _ = super().to_serializable()
        references = {
            "edge": self.edge.uuid if self.edge else None,
            "trip": self.trip.uuid if self.trip else None,
            "additional_signals": [signal.uuid for signal in self.additional_signals],
            "supported_states": [str(state) for state in self.supported_states],
            "direction": str(self.direction),
            "side_distance": self.side_distance,
            "function": str(self.function),
            "kind": str(self.kind),
        }
        objects = dict()
        items = [self.trip] + self.additional_signals if self.trip else self.additional_signals
        for item in items:
            item_object, serialized_item = item.to_serializable()
            objects = {**objects, item.uuid: item_object, **serialized_item}

        return {**attributes, **references}, objects
