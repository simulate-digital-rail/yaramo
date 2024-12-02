from enum import Enum
from itertools import permutations
from math import sin, cos, atan2
import sys

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
        self.connected_on_head = None
        self.connected_on_left = None
        self.connected_on_right = None
        self.maximum_speed_on_left = None
        self.maximum_speed_on_right = None
        self.connected_nodes: list["Node"] = []
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

    def get_anschluss_of_other(self, other: "Node") -> NodeConnectionDirection:
        """Gets the Anschluss (Ende, Links, Rechts, Spitze) of other node.

        Idea: We assume, the current node is a point and we want to estimate the Anschluss of the other node.
        """

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
        """Calculates and sets the 'Anschluss' or connection side of
        the connected_nodes based on their geo location."""

        def get_rad_between_nodes(node_a: GeoPoint, node_b: GeoPoint) -> float:
            """
            Returns the angle of an (maybe imaginary) line between
            :param:`node_a` and :param:`node_b`.
            """
            point_a = node_a.geo_node.geo_point
            point_b = node_b.geo_node.geo_point
            return atan2(point_b.y - point_a.y, point_b.x - point_a.x)

        # Determine which node is head, left, and right by trying the
        # permutations and checking for plausibility.
        for head, left, right in permutations(self.connected_nodes):

            head_angle_abs = get_rad_between_nodes(head, self)

            left_angle_abs = get_rad_between_nodes(self, left)
            left_angle_rel = left_angle_abs - head_angle_abs
            if cos(left_angle_rel) <= sys.float_info.epsilon:
                # left turn more than (or almost) 90°
                continue

            right_angle_abs = get_rad_between_nodes(self, right)
            right_angle_rel = right_angle_abs - head_angle_abs
            if cos(right_angle_rel) <= sys.float_info.epsilon:
                # left turn more than (or almost) 90°
                continue

            if sin(left_angle_rel) < sin(right_angle_rel):
                # Left and right mixed up. Although the permutations do
                # contain the correct combination, fixing this right
                # away potentially saves cycles:
                left, right = right, left

            self.connected_on_head = head
            self.connected_on_left = left
            self.connected_on_right = right
            break

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
        objects = dict()
        if self.geo_node:
            geo_node, serialized_geo_node = self.geo_node.to_serializable()
            objects = {**objects, self.geo_node.uuid: geo_node, **serialized_geo_node}

        return {**attributes, **references}, objects
