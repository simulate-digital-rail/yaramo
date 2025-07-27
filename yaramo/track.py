from collections import Counter
from enum import IntEnum, auto
from typing import Dict, List, Tuple

from yaramo.base_element import BaseElement
from yaramo.edge import Edge
from yaramo.node import Node


class TrackType(IntEnum):
    Durchgehendes_Hauptgleis = auto()
    Hauptgleis = auto()
    Streckengleis = auto()
    Anschlussgleis = auto()
    Nebengleis = auto()
    sonstige = auto()


class Track(BaseElement):
    def __init__(self, track_type, **kwargs):
        super().__init__(**kwargs)
        self.edge_sections: Dict[Edge, Tuple[float, float]] = {}

        if isinstance(track_type, str):
            self.track_type = TrackType.__members__.get(track_type, TrackType.sonstige)
        elif isinstance(track_type, TrackType):
            self.track_type = track_type

    def add_edge_section(self, edge: Edge, section_start: float, section_end: float):
        self.edge_sections[edge] = (section_start, section_end)

    @property
    def edges(self) -> List[Edge]:
        return list(self.edge_sections.keys())

    @property
    def nodes(self) -> List[Node]:
        return list({node for edge in self.edges for node in (edge.node_a, edge.node_b)})

    def get_edges_in_order(self) -> List[Edge]:
        if len(self.edges) <= 1:
            return self.edges

        def _count_node_occurrences_in_edges(_node: Node):
            _count = 0
            for _edge in self.edges:
                if _node == _edge.node_a:
                    _count += 1
                if _node == _edge.node_b:
                    _count += 1
            return _count

        previous_edge: Edge | None = self.edges[0]
        next_node: Node | None = None

        for edge in self.edges:
            count_a = _count_node_occurrences_in_edges(edge.node_a)
            count_b = _count_node_occurrences_in_edges(edge.node_b)
            if count_a == 1 and count_b == 1:
                raise ValueError("Edges of Track separated")
            if count_a == 1 and count_b > 1:
                previous_edge = edge
                next_node = edge.node_b
                break
            if count_a > 1 and count_b == 1:
                previous_edge = edge
                next_node = edge.node_a
                break

        edges_in_order: List[Edge] = [previous_edge]

        while len(edges_in_order) < len(self.edges):
            next_edge = None
            for edge in self.edges:
                if edge.is_node_connected(next_node) and not edge == previous_edge:
                    next_edge = edge
                    break

            edges_in_order.append(next_edge)
            next_node = next_edge.get_other_node(next_node)
            previous_edge = next_edge

        return edges_in_order

    def is_node_in_track(self, node: Node):
        for edge in self.edges:
            if edge.is_node_connected(node):
                return True
        return False
