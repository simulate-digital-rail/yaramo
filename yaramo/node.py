import sys
from enum import Enum
from itertools import permutations
from math import atan2, cos, sin
from typing import List

from yaramo.base_element import BaseElement
from yaramo.geo_node import GeoNode


class EdgeConnectionDirection(Enum):
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
        self.geo_node: GeoNode = kwargs.get("geo_node", None)
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
            self.calc_anschluss_of_all_edges()
        if self.connected_edge_on_head is None:
            return None
        return self.connected_edge_on_head.get_opposite_node(self)

    @property
    def connected_on_left(self):
        if self.connected_edge_on_head is None:
            self.calc_anschluss_of_all_edges()
        if self.connected_edge_on_left is None:
            return None
        return self.connected_edge_on_left.get_opposite_node(self)

    @property
    def connected_on_right(self):
        if self.connected_edge_on_head is None:
            self.calc_anschluss_of_all_edges()
        if self.connected_edge_on_right is None:
            return None
        return self.connected_edge_on_right.get_opposite_node(self)

    def set_connection_head_edge(self, edge: "Edge"):
        self.connected_edge_on_head = edge
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def set_connection_left_edge(self, edge: "Edge"):
        self.connected_edge_on_left = edge
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def set_connection_right_edge(self, edge: "Edge"):
        self.connected_edge_on_right = edge
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def remove_edge(self, edge: "Edge"):
        self.connected_edges.remove(edge)
        if self.connected_edge_on_head == edge:
            self.connected_edge_on_head = None
        if self.connected_edge_on_left == edge:
            self.connected_edge_on_left = None
        if self.connected_edge_on_right == edge:
            self.connected_edge_on_right = None

    def remove_edge_to_node(self, node: "Node"):
        """Removes the edge to the given node and removes the node from the connected_nodes list."""
        edge = self.get_edge_to_node(node)
        self.remove_edge(edge)

    def get_edge_to_node(self, node):
        """Returns the edge to the given neighbor node."""
        return next(edge for edge in self.connected_edges if edge.get_opposite_node(self) == node)

    def get_possible_followers(self, source: "Edge") -> List["Edge"]:
        """Returns the `Edge`s that could follow (head, left, right) when comming from a source `Edge` connected to this `Node`."""
        if source is None:
            return self.connected_edges

        if len(self.connected_edges) <= 1:
            return []

        if self.connected_edge_on_head is None:
            self.calc_anschluss_of_all_edges()

        if source == self.connected_edge_on_head:
            return [self.connected_edge_on_left, self.connected_edge_on_right]
        return [self.connected_edge_on_head]

    def get_anschluss_for_edge(self, edge: "Edge") -> EdgeConnectionDirection:
        """Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node.
        Idea: We assume, the current node is a point and we want to estimate the Anschluss of the other node.

        :return: A node might be connected to the same node via two or more connections. So we return a list of connections.
        """

        if len(self.connected_edges) != 3:
            raise Exception(f"Try to get Anschluss of Ende (Node ID: {self.uuid})")

        # TODO allow for different metrics to estimate the anschluss of the other nodes
        if not all([self.connected_on_left, self.connected_on_right, self.connected_on_head]):
            self.calc_anschluss_of_all_edges()

        if edge.uuid == self.connected_edge_on_head.uuid:
            return EdgeConnectionDirection.Spitze
        if edge.uuid == self.connected_edge_on_left.uuid:
            return EdgeConnectionDirection.Links
        if edge.uuid == self.connected_edge_on_right.uuid:
            return EdgeConnectionDirection.Rechts
        return None

    def calc_anschluss_of_all_edges(self):
        """Calculates and sets the 'Anschluss' or connection side of
        the connected_nodes based on their geo location."""

        if len(self.connected_edges) == 1:
            self.connected_edge_on_head = self.connected_edges[0]
            return

        def get_arc_between_geo_nodes(geo_node_a: "GeoNode", geo_node_b: "GeoNode") -> float:
            """
            Returns the angle of an (maybe imaginary) line between
            :param:`node_a` and :param:`node_b`.
            """
            return atan2(geo_node_b.y - geo_node_a.y, geo_node_b.x - geo_node_a.x)

        # Determine which node is head, left, and right by trying the
        # permutations and checking for plausibility.
        for head, left, right in permutations(self.connected_edges):

            head_angle_abs = get_arc_between_geo_nodes(head.get_next_geo_node(self), self.geo_node)
            left_angle_abs = get_arc_between_geo_nodes(self.geo_node, left.get_next_geo_node(self))
            left_angle_rel = left_angle_abs - head_angle_abs
            if cos(left_angle_rel) <= sys.float_info.epsilon:
                # left turn more than (or almost) 90°
                continue

            right_angle_abs = get_arc_between_geo_nodes(
                self.geo_node, right.get_next_geo_node(self)
            )
            right_angle_rel = right_angle_abs - head_angle_abs
            if cos(right_angle_rel) <= sys.float_info.epsilon:
                # left turn more than (or almost) 90°
                continue

            if sin(left_angle_rel) < sin(right_angle_rel):
                # Left and right mixed up. Although the permutations do
                # contain the correct combination, fixing this right
                # away potentially saves cycles:
                left, right = right, left

            self.connected_edge_on_head = head
            self.connected_edge_on_left = left
            self.connected_edge_on_right = right
            break

    def is_point(self):
        """
        Returns true if this node is a point.
        A point is a `Node` with at least 3 connected tracks (yaramo only supports three edges at the moment)
        """
        return len(self.connected_edges) >= 3

    def to_serializable(self):
        """See the description in the BaseElement class.

        Returns:
            A serializable dictionary and a dictionary with serialized objects (GeoNodes).
        """

        attributes = self.__dict__
        references = {
            "connected_edge_on_head": self.connected_edge_on_head.uuid
            if self.connected_edge_on_head
            else None,
            "connected_edge_on_left": self.connected_edge_on_left.uuid
            if self.connected_edge_on_left
            else None,
            "connected_edge_on_right": self.connected_edge_on_right.uuid
            if self.connected_edge_on_right
            else None,
            "connected_on_head": self.connected_on_head.uuid if self.connected_on_head else None,
            "connected_on_left": self.connected_on_left.uuid if self.connected_on_left else None,
            "connected_on_right": self.connected_on_right.uuid if self.connected_on_right else None,
            "connected_nodes": [node.uuid for node in self.connected_nodes],
            "connected_edges": [edge.uuid for edge in self.connected_edges],
            "geo_node": self.geo_node.uuid if self.geo_node else None,
        }
        objects = dict()
        if self.geo_node:
            geo_node, serialized_geo_node = self.geo_node.to_serializable()
            objects = {**objects, self.geo_node.uuid: geo_node, **serialized_geo_node}

        return {**attributes, **references}, objects
