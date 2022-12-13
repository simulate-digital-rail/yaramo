from decimal import Decimal
from enum import Enum
import math
from yaramo.base_element import BaseElement
from yaramo.geo_node import DistanceFunction, GeoNode


class NodeConnectionDirection(Enum):
    Spitze = 0
    Links = 1
    Rechts = 2


class Node(BaseElement):

    def __init__(self, distance_function: DistanceFunction = None, **kwargs):
        super().__init__(**kwargs)
        self.connected_on_head = None
        self.connected_on_left = None
        self.connected_on_right = None
        self.connected_nodes: list['Node'] = []
        self.geo_node: GeoNode = None
        self.distance_function = distance_function or DistanceFunction.Euclidean

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

        if len(self.connected_nodes) <= 1:
            return []

        if self.connected_on_head is None:
            self.calc_anschluss_of_all_nodes()

        if source.uuid == self.connected_on_head.uuid:
            return [self.connected_on_left, self.connected_on_right]
        else:
            return [self.connected_on_head]

    def get_anschluss_of_other(self, other: 'Node') -> NodeConnectionDirection:
        #  Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node. Idea: We assume, the current node is a point
        #  and we want to estimate the Anschluss of the other node.
        if len(self.connected_nodes) != 3:
            print(f"Try to get Anschluss of Ende (Node ID: {self.identifier})")
            return None

        # TODO allow for different metrics to estimate the anschluss of the other nodes
        if any(self.connected_nodes, lambda x: x is None):
            self.calc_anschluss_of_all_nodes()

        if other.uuid == self.connected_on_head.uuid:
            return NodeConnectionDirection.Spitze
        if other.uuid == self.connected_on_left.uuid:
            return NodeConnectionDirection.Links
        if other.uuid == self.connected_on_right.uuid:
            return NodeConnectionDirection.Rechts
        return None

    def calc_anschluss_of_all_nodes(self):

        def get_arc_between_nodes(_node_a: 'Node', _node_b: 'Node'):
            _a = _node_a.geo_node.get_distance_to_other_geo_node(
                self.geo_node, distance_function=self.distance_function)
            _b = self.geo_node.get_distance_to_other_geo_node(
                _node_b.geo_node, distance_function=self.distance_function)
            _c = _node_a.geo_node.get_distance_to_other_geo_node(
                _node_b.geo_node, distance_function=self.distance_function)

            return math.degrees(math.acos((_a * _a + _b * _b - _c * _c) / (2.0 * _a * _b)))

        current_max_arc = 361
        other_a: 'Node' = None
        other_b: 'Node' = None
        for i in range(len(self.connected_nodes)):
            for j in range(len(self.connected_nodes)):
                if i != j:
                    cur_arc = get_arc_between_nodes(
                        self.connected_nodes[i], self.connected_nodes[j])
                    if cur_arc < current_max_arc:
                        missing_index = sum(
                            range(len(self.connected_nodes))) - (i + j)
                        self.tip_node = self.connected_nodes[missing_index]
                        other_a = self.connected_nodes[i]
                        other_b = self.connected_nodes[j]
                        current_max_arc = cur_arc

        other_a_x = other_a.geo_node.geo_point.x
        other_a_y = other_a.geo_node.geo_point.y
        other_b_x = other_b.geo_node.geo_point.x
        other_b_y = other_b.geo_node.geo_point.y
        self_x = self.geo_node.geo_point.x
        self_y = self.geo_node.geo_point.y
        # TODO: Replace this heuristic to determine which node is left and which is right with some suitable algorithm
        if (
            (other_a_x < self_x and other_b_x < self_x) or
            (other_a_x >= self_x and other_b_x >= self_x) or
            (other_a_y < self_y and other_b_y < self_y) or
            (other_a_y >= self_y and other_b_y >= self_y)
        ):
            self.left_node, self.right_node = other_a, other_b
        else:
            self.left_node, self.right_node = other_a, other_b
