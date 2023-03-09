import math
from enum import Enum

from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode
from yaramo.geo_point import GeoPoint


class NodeConnectionDirection(Enum):
    Spitze = 0
    Links = 1
    Rechts = 2


class Node(BaseElement):
    def __init__(self, turnout_side=None, **kwargs):
        super().__init__(**kwargs)
        self.connected_on_head = None
        self.connected_on_left = None
        self.connected_on_right = None
        self.maximum_speed_on_left = None
        self.maximum_speed_on_right = None
        self.connected_nodes: list["Node"] = []
        self.geo_node: GeoNode = None
        self.turnout_side: str = turnout_side

    def maximum_speed(self, node_a: "Node", node_b: "Node"):
        """Return the maximum allowed speed for traversing this node,
        coming from node_a and going to node_b
        """
        if node_a == self.connected_on_left or node_b == self.connected_on_left:
            return self.maximum_speed_on_left
        elif node_a == self.connected_on_right or node_b == self.connected_on_right:
            return self.maximum_speed_on_right
        else:
            return None

    def set_connection_head(self, node: "Node"):
        self.connected_on_head = node
        self.connected_nodes.append(node)

    def set_connection_left(self, node: "Node"):
        self.connected_on_left = node
        self.connected_nodes.append(node)

    def set_connection_right(self, node: "Node"):
        self.connected_on_right = node
        self.connected_nodes.append(node)

    def get_possible_followers(self, source):
        if source is None:
            return self.connected_nodes

        if len(self.connected_nodes) <= 1:
            return []

        if self.connected_on_head is None:
            self.calc_anschluss_of_all_nodes()

        if source.uuid == self.connected_on_head.uuid:
            return [self.connected_on_left, self.connected_on_right]
        else:
            return [self.connected_on_head]

    def get_anschluss_of_other(self, other: "Node") -> NodeConnectionDirection:
        #  Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node. Idea: We assume, the current node is a point
        #  and we want to estimate the Anschluss of the other node.
        if len(self.connected_nodes) != 3:
            raise Exception(f"Try to get Anschluss of Ende (Node ID: {self.uuid})")

        # TODO allow for different metrics to estimate the anschluss of the other nodes
        if not all([self.connected_on_left, self.connected_on_right, self.connected_on_head]):
            self.calc_anschluss_of_all_nodes()

        if other.uuid == self.connected_on_head.uuid:
            return NodeConnectionDirection.Spitze
        if other.uuid == self.connected_on_left.uuid:
            return NodeConnectionDirection.Links
        if other.uuid == self.connected_on_right.uuid:
            return NodeConnectionDirection.Rechts
        return None

    def calc_anschluss_of_all_nodes(self):
        def get_arc_between_nodes(_node_a: "Node", _node_b: "Node"):
            _a = _node_a.geo_node.get_distance_to_other_geo_node(self.geo_node)
            _b = self.geo_node.get_distance_to_other_geo_node(_node_b.geo_node)
            _c = _node_a.geo_node.get_distance_to_other_geo_node(_node_b.geo_node)

            return math.degrees(math.acos((_a * _a + _b * _b - _c * _c) / (2.0 * _a * _b)))
        
        def is_above_line_between_points(head_point: GeoPoint, branching_point: GeoPoint, comparison_point: GeoPoint):
            return ((branching_point.x - head_point.x)*(comparison_point.y - head_point.y) - (branching_point.y - head_point.y)*(comparison_point.x - head_point.x)) > 0

        current_max_arc = 361
        other_a: "Node" = None
        other_b: "Node" = None
        for i in range(len(self.connected_nodes)):
            for j in range(len(self.connected_nodes)):
                if i != j:
                    cur_arc = get_arc_between_nodes(
                        self.connected_nodes[i], self.connected_nodes[j]
                    )
                    if cur_arc < current_max_arc:
                        missing_index = sum(range(len(self.connected_nodes))) - (i + j)
                        self.connected_on_head = self.connected_nodes[missing_index]
                        other_a = self.connected_nodes[i]
                        other_b = self.connected_nodes[j]
                        current_max_arc = cur_arc

        if (is_above_line_between_points(self.connected_on_head.geo_node.geo_point, self.geo_node.geo_point, other_a.geo_node.geo_point)):
            self.connected_on_left, self.connected_on_right = other_a, other_b
        else:
            self.connected_on_right, self.connected_on_left = other_a, other_b

    def to_serializable(self):
        attributes = self.__dict__
        references = {
            "connected_on_head": self.connected_on_head.uuid if self.connected_on_head else None,
            "connected_on_left": self.connected_on_left.uuid if self.connected_on_left else None,
            "connected_on_right": self.connected_on_right.uuid if self.connected_on_right else None,
            "connected_nodes": [node.uuid for node in self.connected_nodes],
            "geo_node": self.geo_node.uuid if self.geo_node else None,
        }
        objects = {}
        if self.geo_node:
            geo_node, serialized_geo_node = self.geo_node.to_serializable()
            objects = {**objects, self.geo_node.uuid: geo_node, **serialized_geo_node}

        return {**attributes, **references}, objects
