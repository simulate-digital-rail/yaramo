from enum import Enum
import math
from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode

class NodeConnectionDirection(Enum):
    Spitze = 0
    Links = 1
    Rechts = 2

class Node(BaseElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connected_on_head = None
        self.connected_on_left = None
        self.connected_on_right = None
        self.connected_nodes: list[GeoNode] = []
        self.geo_node: GeoNode = None

    def set_connection_head(self, node: 'Node'):
        self.connected_on_head = node
        self.connected_nodes.append(node)

    def set_connection_left(self, node: 'Node'):
        self.connected_on_left = node
        self.connected_nodes.append(node)

    def set_connection_right(self, node: 'Node'):
        self.connected_on_right = node
        self.connected_nodes.append(node)

    def get_possible_followers(self, source):
        if source is None:
            return self.connected_nodes

        if len(self.connected_nodes) == 1:
            return []

        if source.uuid == self.connected_on_head.uuid:
            return [self.connected_on_left, self.connected_on_right]
        else:
            return [self.connected_on_head]

    def get_anschluss_of_other(self, other: 'Node'):
        #  Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node. Idea: We assume, the current node is a point
        #  and we want to estimate the Anschluss of the other node.
        if len(self.connected_nodes) != 3:
            print(f"Try to get Anschluss of Ende (Node ID: {self.identifier})")
            return None

        # TODO allow for different metrics to estimate the anschluss of the other nodes
        if any(self.connected_nodes, lambda x : x is None):
            return None
        
        if other.uuid == self.connected_on_head.uuid:
            return NodeConnectionDirection.Spitze
        if other.uuid == self.connected_on_left.uuid:
            return NodeConnectionDirection.Links
        if other.uuid == self.connected_on_right.uuid:
            return NodeConnectionDirection.Rechts
        return None
