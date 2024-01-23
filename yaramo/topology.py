import json

from yaramo.base_element import BaseElement
from yaramo.edge import Edge
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

    def add_node(self, node: Node):
        self.nodes[node.uuid] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.uuid] = edge

    def add_signal(self, signal: Signal):
        self.signals[signal.uuid] = signal

    def add_route(self, route: Route):
        self.routes[route.uuid] = route

    def add_vacancy_section(self, vacancy_section: VacancySection):
        self.vacancy_sections[vacancy_section.uuid] = vacancy_section

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
            "vacany_sections": vacancy_sections
        }, {}

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str)
        topology = cls()
        for node in obj["nodes"]:
            topology.add_node(Node(**node))
        for signal in obj["signals"]:
            topology.add_signal(Signal(**signal))
        for edge in obj["edges"]:
            node_a = topology.nodes[edge["node_a"]]
            node_b = topology.nodes[edge["node_b"]]
            node_a.connected_nodes.append(node_b)
            node_b.connected_nodes.append(node_a)
            topology.add_edge(Edge(**{
                **edge, "node_a": node_a, "node_b": node_b,
                "signals": [topology.signals[signal_uuid] for signal_uuid in edge["signals"]],
                "intermediate_geo_nodes": [obj["objects"][geo_node_uuid] for geo_node_uuid in edge["intermediate_geo_nodes"] if geo_node_uuid in obj["objects"]],
            }))
        for signal in obj["signals"]:
            topology.signals[signal["uuid"]].edge = topology.edges[signal["edge"]]
        return topology


if __name__ == "__main__":
    with open("../test.json", "r") as f:
        json_str = f.read()
    topology = Topology.from_json(json_str)
    print(topology.to_json())
