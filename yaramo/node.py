import math
from enum import Enum
from typing import List

from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode
from yaramo.geo_point import GeoPoint


class NodeConnectionDirection(Enum):
    Spitze = 0
    Links = 1
    Rechts = 2


class Node(BaseElement):
    """This class is one of two Elements (Edge and Node) comprising the base of the yaramo Topology.

    A Node can be connected to other Nodes on it's head, left and right connection.
    We assume that there are only Nodes connected on all three or only one connection.
    There can be a GeoNode associated with a Node to add a geo-location.
    """
     
    def __init__(self, turnout_side=None, **kwargs):
        """
        Parameters
        ----------
        maximum_speed_on_left, maximum_speed_on_right: int
            The allowed maximum speed going over that connection
        turnout_side: str
            The connection side (left or right) that branches away on the real track
        """

        super().__init__(**kwargs)
        self.connected_edge_on_head = None
        self.connected_edge_on_right = None
        self.connected_edge_on_left = None
        self.maximum_speed_on_left = None
        self.maximum_speed_on_right = None
        self.connected_edges: list["Edge"] = []
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

    @property
    def connected_nodes(self):
        return [edge.get_opposite_node(self) for edge in self.connected_edges]

    @property
    def connected_on_head(self):
        if self.connected_edge_on_head is None:
            return None
        return self.connected_edge_on_head.get_opposite_node(self)

    @property
    def connected_on_left(self):
        if self.connected_edge_on_left is None:
            return None
        return self.connected_edge_on_left.get_opposite_node(self)

    @property
    def connected_on_right(self):
        if self.connected_edge_on_right is None:
            return None
        return self.connected_edge_on_right.get_opposite_node(self)

    def set_connection_head_edge(self, edge: "Edge"):
        self.connected_edge_on_head = edge
        self.connected_edges.append(edge)

    def set_connection_left_edge(self, edge: "Edge"):

        self.connected_edge_on_left = edge
        self.connected_edges.append(edge)

    def set_connection_right_edge(self, edge: "Edge"):
        self.connected_edge_on_right = edge
        self.connected_edges.append(edge)

    def remove_edge_to_node(self, node: "Node"):
        """Removes the edge to the given node and removes the node from the connected_nodes list."""
        edge = self.get_edge_to_node(node)
        self.connected_edges.remove(edge)

    def get_edge_to_node(self, node):
        """Returns the edge to the given neighbor node."""
        return next(edge for edge in self.connected_edges if edge.get_opposite_node(self) == node)

    def get_possible_followers(self, source):
        """Returns the Nodes that could follow (head, left, right) when comming from a source Node connected to this Node."""
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

    def get_anschluss_for_edge(self, edge: "Edge") -> NodeConnectionDirection:
        """Gets the Anschluss (Links, Rechts, Spitze) of the edge on the current node.

        :return: The node connection
        """

        if self.connected_edge_on_head == edge:
            return NodeConnectionDirection.Spitze
        if self.connected_edge_on_left == edge:
            return NodeConnectionDirection.Links
        if self.connected_edge_on_right == edge:
            return NodeConnectionDirection.Rechts

        return None

    def get_anschluss_of_other(self, other: "Node") -> List[NodeConnectionDirection]:
        """Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node.
         
        Idea: We assume, the current node is a point and we want to estimate the Anschluss of the other node.

        :return: A node might be connected to the same node via two or more connections. So we return a list of connections.
        """

        if len(self.connected_nodes) != 3:
            raise Exception(f"Try to get Anschluss of Ende (Node ID: {self.uuid})")

        # TODO allow for different metrics to estimate the anschluss of the other nodes
        if not all([self.connected_on_left, self.connected_on_right, self.connected_on_head]):
            self.calc_anschluss_of_all_nodes()

        result = []

        if other.uuid == self.connected_on_head.uuid:
            result.append(NodeConnectionDirection.Spitze)
        if other.uuid == self.connected_on_left.uuid:
            result.append(NodeConnectionDirection.Links)
        if other.uuid == self.connected_on_right.uuid:
            result.append(NodeConnectionDirection.Rechts)
        
        if len(result) == 0:
            return None

        return result

    def calc_anschluss_of_all_nodes(self):
        """Calculates and sets the 'Anschluss' or connection side of the connected_nodes based on their geo-location."""

        def get_arc_between_nodes(_node_a: "Node", _node_b: "Node"):
            _neighbor_to_a = self.get_edge_to_node(_node_a).get_next_geo_node(self)
            _neighbor_to_b = self.get_edge_to_node(_node_b).get_next_geo_node(self)
            _a = _neighbor_to_a.get_distance_to_other_geo_node(self.geo_node)
            _b = self.geo_node.get_distance_to_other_geo_node(_neighbor_to_b)
            _c = _neighbor_to_a.get_distance_to_other_geo_node(_neighbor_to_b)

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
                        self.connected_edge_on_head = self.get_edge_to_node(
                            self.connected_nodes[missing_index]
                        )
                        other_a = self.connected_nodes[i]
                        other_b = self.connected_nodes[j]
                        current_max_arc = cur_arc

        _neighbor_to_head = self.connected_edge_on_head.get_next_geo_node(self)
        _neighbor_to_a = self.get_edge_to_node(other_a).get_next_geo_node(self)
        _neighbor_to_b = self.get_edge_to_node(other_b).get_next_geo_node(self)
        # Check on which side of the line between the head connection and this node the other nodes are
        side_a = is_above_line_between_points(
            _neighbor_to_head.geo_point,
            self.geo_node.geo_point,
            _neighbor_to_a.geo_point,
        )
        side_b = is_above_line_between_points(
            _neighbor_to_head.geo_point,
            self.geo_node.geo_point,
            _neighbor_to_b.geo_point,
        )

        # If they're on two separate sides we know which is left and right
        if side_a != side_b:
            if side_a:
                self.connected_edge_on_left = self.get_edge_to_node(other_a)
                self.connected_edge_on_right = self.get_edge_to_node(other_b)
            else:
                self.connected_edge_on_left = self.get_edge_to_node(other_b)
                self.connected_edge_on_right = self.get_edge_to_node(other_a)
        # If they're both above or below that line, we make the node that branches further away the left or right node,
        # depending on the side they're on (left if both above)
        else:
            arc_a = get_arc_between_nodes(self.connected_on_head, other_a)
            arc_b = get_arc_between_nodes(self.connected_on_head, other_b)
            if arc_a > arc_b:
                self.connected_edge_on_left = (
                    self.get_edge_to_node(other_b) if side_a else self.get_edge_to_node(other_a)
                )
                self.connected_edge_on_right = (
                    self.get_edge_to_node(other_a) if side_a else self.get_edge_to_node(other_b)
                )
            else:
                self.connected_edge_on_left = (
                    self.get_edge_to_node(other_a) if side_a else self.get_edge_to_node(other_b)
                )
                self.connected_edge_on_right = (
                    self.get_edge_to_node(other_b) if side_a else self.get_edge_to_node(other_a)
                )

    def to_serializable(self):
        """See the description in the BaseElement class.

        Returns:
            A serializable dictionary and a dictionary with serialized objects (GeoNodes).
        """
        
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
