from typing import List, Optional

from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode
from yaramo.node import Node
from yaramo.vacancy_section import VacancySection


class Edge(BaseElement):
    """This class is one of two Elements (Edge and Node) comprising the base of the yaramo Topology.

    An Edge is fundamentally defined by two Nodes (a and b). It does have a list of GeoNodes and a list of Signals
    that may be on that Edge. An Edge can have a length set on construction, however if that is not the case, 
    the length can be calculated by calling update_length(). This sets the length based on the GeoNodes referred to by node_a and node_b
    as well as any intermediate_geo_nodes. The maximum_speed of an Edge cannot be set on construction but will generally be determined based on the connected Topology and Signals.
    """

    def __init__(self, node_a: Node, node_b: Node, vacancy_section: Optional[VacancySection] = None, length: float = None, **kwargs):
        """
        Parameters
        ----------
        node_a : Node
            The first Node connecting the Edge
        node_b : Node
            The second Node connecting the Edge
        vacancy_section: Optional[VacancySection]
            A possible reference to a VacancySection the Edge belongs to (default is None)
        length: float
            The length of the edge (default is None)
        """

        super().__init__(**kwargs)
        self.node_a = node_a
        self.node_b = node_b
        self.intermediate_geo_nodes: list[GeoNode] = []
        self.signals: list[Signal] = []
        self.length = length
        self.maximum_speed: int = None
        self.vacancy_section = vacancy_section

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

        total_length = self.node_a.geo_node.get_distance_to_other_geo_node(
            self.intermediate_geo_nodes[0]
        )

        for i in range(len(self.intermediate_geo_nodes) - 1):
            geo_node_a = self.intermediate_geo_nodes[i]
            geo_node_b = self.intermediate_geo_nodes[i + 1]
            total_length += geo_node_a.get_distance_to_other_geo_node(geo_node_b)

        total_length += self.intermediate_geo_nodes[-1].get_distance_to_other_geo_node(
            self.node_b.geo_node
        )
        return total_length

    def get_direction_based_on_nodes(self, node_a: "Node", node_b: "Node") -> "SignalDirection":
        """Returns the a direction according to whether the order of node_a and node_b is the same as in self

        Parameters
        ----------
        node_a : Node
            The first Node to compare
        node_b : Node
            The second Node to compare

        Returns
        -------
        SignalDirection
            SignalDirection.IN or SignalDirection.GEGEN depending on the relative direction
        """

        from yaramo.signal import SignalDirection

        if self.node_a.uuid == node_a.uuid and self.node_b.uuid == node_b.uuid:
            return SignalDirection.IN
        elif self.node_a.uuid == node_b.uuid and self.node_b.uuid == node_a.uuid:
            return SignalDirection.GEGEN
        return None

    def get_signals_with_direction_in_order(self, direction: "SignalDirection") -> List["Signal"]:
        """Returns all the signals (with that direction) on that Edge ordered by the given direction

        This only consideres Signals of SignalFunction type Einfahr_Signal, Ausfahr_Signal and Block_Signal that have the same direction as requested.
        Parameters
        ----------
        direction : SignalDirection
            The direction of collecting the signals (Starting at self.node_a is IN direction)

        Returns
        -------
        List["Signal"]
        """

        from yaramo.signal import SignalDirection, SignalFunction

        result: list[Signal] = []
        for signal in self.signals:
            if (
                signal.function
                in [
                    SignalFunction.Einfahr_Signal,
                    SignalFunction.Ausfahr_Signal,
                    SignalFunction.Block_Signal,
                ]
                and signal.direction == direction
            ):
                result.append(signal)
        result.sort(key=lambda x: x.distance_edge, reverse=(direction == SignalDirection.GEGEN))
        return result

    def to_serializable(self):
        """Creates two serializable dictionaries out of the Edge object.

        This creates a dictionary with immediately serializable attributes and
        references (uuids) to attributes that are objects.
        This creates a second dictionary where said objects are serialized (by deligation).

        See the description in the BaseElement class.

        Returns:
            A serializable dictionary and a dictionary with serialized objects (GeoNodes).
        """

        attributes = self.__dict__
        references = {
            "node_a": self.node_a.uuid,
            "node_b": self.node_b.uuid,
            "intermediate_geo_nodes": [geo_node.uuid for geo_node in self.intermediate_geo_nodes],
            "signals": [signal.uuid for signal in self.signals],
        }
        objects = {}
        for geo_node in self.intermediate_geo_nodes:
            geo_node_object, serialized_geo_node = geo_node.to_serializable()
            objects = {**objects, geo_node.uuid: geo_node_object, **serialized_geo_node}

        return {**attributes, **references}, objects
