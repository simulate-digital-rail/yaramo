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
        objects = {}

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
