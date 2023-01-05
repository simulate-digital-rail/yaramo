from yaramo.base_element import BaseElement
from yaramo.node import Node
from yaramo.edge import Edge
from yaramo.route import Route
from yaramo.signal import Signal

class Topology(BaseElement):

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.signals: dict[str, Signal] = {}
        self.routes: list[Route] = []

    def add_node(self, node: Node):
        self.nodes[node.uuid] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.uuid] = edge

    def add_signal(self, signal: Signal):
        self.signals[signal.uuid] = signal

    def add_route(self, route: Route):
        self.routes[route.uuid] = route

    def get_edge_by_nodes(self, node_a: Node, node_b: Node):
        for edge_uuid in self.edges:
            edge = self.edges[edge_uuid]
            if edge.node_a.uuid == node_a.uuid and edge.node_b.uuid == node_b.uuid or \
               edge.node_a.uuid == node_b.uuid and edge.node_b.uuid == node_a.uuid:
                return edge
        return None

    def to_serializable(self):
        nodes = []
        edges = []
        signals = []
        objects = {}
        for node in self.nodes.values():
            reference, serialized = node.to_serializable()
            nodes.append(reference)
            objects = {**objects, **serialized}
        for edge in self.edges.values():
            reference, serialized = edge.to_serializable()
            edges.append(reference)
            objects = {**objects, **serialized}
        for signal in self.signals.values():
            reference, serialized = signal.to_serializable()
            signals.append(reference)
            objects = {**objects, **serialized}

        return {
            'nodes': nodes,
            'edges': edges,
            'signals': signals,
            'objects': objects
        }

