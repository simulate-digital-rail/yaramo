from datetime import datetime
from typing import List

import simplejson as json

from yaramo.base_element import BaseElement
from yaramo.edge import Edge
from yaramo.geo_node import Wgs84GeoNode
from yaramo.node import Node
from yaramo.route import Route
from yaramo.signal import Signal
from yaramo.vacancy_section import VacancySection


class Topology(BaseElement):
    """The Topology is a collection of all track elements comprising that topology.

    Elements like Signals, Nodes, Edges, Routes and Vacancy Sections can be accessed by their uuid in their respective dictionary.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.signals: dict[str, Signal] = {}
        self.routes: dict[str, Route] = {}
        self.vacancy_sections: dict[str, VacancySection] = {}

        self.created_at: datetime = datetime.now()
        self.created_with: str = "unknown"

    def add_node(self, node: Node):
        self.nodes[node.uuid] = node

    def add_nodes(self, nodes: List[Node]):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: Edge):
        self.edges[edge.uuid] = edge

    def add_edges(self, edges: List[Edge]):
        for edge in edges:
            self.add_edge(edge)

    def add_signal(self, signal: Signal):
        self.signals[signal.uuid] = signal

    def add_signals(self, signals: List[Signal]):
        for signal in signals:
            self.add_signal(signal)

    def add_route(self, route: Route):
        self.routes[route.uuid] = route

    def add_routes(self, routes: List[Route]):
        for route in routes:
            self.add_route(route)

    def add_vacancy_section(self, vacancy_section: VacancySection):
        self.vacancy_sections[vacancy_section.uuid] = vacancy_section

    def add_vavancy_sections(self, vacancy_sections: List[VacancySection]):
        for vacancy_section in vacancy_sections:
            self.add_vacancy_section(vacancy_section)

    def get_edge_by_nodes(self, node_a: Node, node_b: Node):
        for edge_uuid in self.edges:
            edge = self.edges[edge_uuid]
            if (
                edge.node_a.uuid == node_a.uuid
                and edge.node_b.uuid == node_b.uuid
                or edge.node_a.uuid == node_b.uuid
                and edge.node_b.uuid == node_a.uuid
            ):
                return edge
        return None

    def to_serializable(self):
        """See the description in the BaseElement class.

        Returns:
            A serializable dictionary of all the objects belonging to the Topology.
        """
        nodes, edges, signals, routes, vacancy_sections = [], [], [], [], []
        objects = dict()

        for items, _list in [
            (list(self.signals.values()), signals),
            (list(self.nodes.values()), nodes),
            (list(self.edges.values()), edges),
            (list(self.routes.values()), routes),
            (list(self.vacancy_sections.values()), vacancy_sections),
        ]:
            for item in items:
                reference, serialized = item.to_serializable()
                _list.append(reference)
                objects = {**objects, **serialized}

        return {
            "nodes": nodes,
            "edges": edges,
            "signals": signals,
            "routes": routes,
            "objects": objects,
            "vacany_sections": vacancy_sections,
        }, {}

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str)
        topology = cls()
        for node in obj["nodes"]:
            node_obj = Node(**node)
            topology.add_node(node_obj)
            if "geo_node" in node and node["geo_node"] is not None:
                geo_node = obj["objects"][node["geo_node"]]
                geo_node_obj = Wgs84GeoNode(
                    obj["objects"][geo_node["geo_point"]]["x"],
                    obj["objects"][geo_node["geo_point"]]["y"],
                    name=geo_node["name"],
                    uuid=geo_node["uuid"],
                )
                node_obj.geo_node = geo_node_obj

        for signal in obj["signals"]:
            topology.add_signal(Signal(**signal))
        for edge in obj["edges"]:
            node_a = topology.nodes[edge["node_a"]]
            node_b = topology.nodes[edge["node_b"]]
            node_a.connected_nodes.append(node_b)
            node_b.connected_nodes.append(node_a)
            geo_node_strings = [
                obj["objects"][geo_node_uuid]
                for geo_node_uuid in edge["intermediate_geo_nodes"]
                if geo_node_uuid in obj["objects"]
            ]
            topology.add_edge(
                Edge(
                    **{
                        **edge,
                        "node_a": node_a,
                        "node_b": node_b,
                        "signals": [
                            topology.signals[signal_uuid] for signal_uuid in edge["signals"]
                        ],
                        "intermediate_geo_nodes": [
                            Wgs84GeoNode(
                                obj["objects"][geo_node["geo_point"]]["x"],
                                obj["objects"][geo_node["geo_point"]]["y"],
                                name=geo_node["name"],
                                uuid=geo_node["uuid"],
                            )
                            for geo_node in geo_node_strings
                        ],
                    }
                )
            )
        for signal in obj["signals"]:
            topology.signals[signal["uuid"]].edge = topology.edges[signal["edge"]]
        return topology
