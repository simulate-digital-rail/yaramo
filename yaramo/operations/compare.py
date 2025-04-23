from enum import Enum, auto
from typing import Dict, List, Set, Tuple

import networkx as nx

from ..model import (
    DbrefGeoNode,
    Edge,
    GeoNode,
    Node,
    Signal,
    SignalDirection,
    Topology,
    Wgs84GeoNode,
)


class CompareMatching:
    def __init__(self):
        self.element_matching = {}
        self.not_found_in_a = []
        self.not_found_in_b = []


class CompareResult:
    def __init__(self):
        self.node_distance: float = -1.0
        self.node_matching: CompareMatching = CompareMatching()
        self.edge_length_difference: float = -1.0
        self.edge_matching: CompareMatching = CompareMatching()
        self.signal_distance: float = -1.0
        self.signal_matching: CompareMatching = CompareMatching()


class CompareMode(Enum):
    EXACT = auto()
    ISOMORPHIC = auto()


class Compare:
    @staticmethod
    def compare(
        topology_a: Topology,
        topology_b: Topology,
        compare_mode: CompareMode,
        given_node_matching: Dict[Node, Node] | None = None,
        exclude_ends_in_calculation: bool = False,
        skip_signals: bool = False,
    ) -> CompareResult:
        if given_node_matching is None:
            given_node_matching = {}

        result: CompareResult = CompareResult()

        if compare_mode == CompareMode.EXACT:
            Compare._calc_exact_matching(result, topology_a, topology_b)
        if compare_mode == CompareMode.ISOMORPHIC:
            if not Compare._are_topologies_isomorphic(topology_a, topology_b):
                raise ValueError("Both topologies needs to be isomorphic")
            if not given_node_matching:
                raise ValueError(
                    "For isomorphic topologies, at least one mathing node needs to be given."
                )
            Compare._calc_isomorphic_matching(
                result, topology_a, topology_b, given_node_matching, skip_signals
            )

        result.node_distance = Compare._calc_distance_for_matching(
            result.node_matching,
            exclude_ends_in_calculation,
            start_node_a=list(given_node_matching.keys())[0],
            start_node_b=list(given_node_matching.values())[0],
        )
        result.edge_length_difference = Compare._calc_distance_for_matching(
            result.edge_matching, exclude_ends_in_calculation, element_type="edge"
        )
        if not skip_signals:
            result.signal_distance = Compare._calc_distance_for_matching(
                result.signal_matching, exclude_ends_in_calculation, element_type="signal"
            )
        return result

    @staticmethod
    def _calc_exact_matching(result: CompareResult, topology_a: Topology, topology_b: Topology):
        Compare._calc_exact_element_matching(
            result.node_matching, topology_a.nodes, topology_b.nodes
        )
        Compare._calc_exact_element_matching(
            result.edge_matching, topology_a.edges, topology_b.edges
        )
        Compare._calc_exact_element_matching(
            result.signal_matching, topology_a.signals, topology_b.signals
        )

    @staticmethod
    def _calc_exact_element_matching(
        compare_matching: CompareMatching, element_dict_a: Dict, element_dict_b: Dict
    ):
        for element_uuid_a, element_a in element_dict_a.items():
            if element_uuid_a in element_dict_b:
                compare_matching.element_matching[element_a] = element_dict_b[element_uuid_a]
            else:
                compare_matching.not_found_in_b.append(element_a)
        for element_uuid_b in element_dict_b.keys() - element_dict_a.keys():
            compare_matching.not_found_in_a.append(element_dict_b[element_uuid_b])

    @staticmethod
    def _calc_isomorphic_matching(
        result: CompareResult,
        topology_a: Topology,
        topology_b: Topology,
        given_node_matching: Dict[Node, Node],
        skip_signals: bool,
    ):
        open_nodes: List[Tuple[Node, Node]] = []

        def __add_to_open_nodes(__node_a: Node, __node_b: Node):
            if __node_a is None and __node_b is None:
                raise ValueError(
                    "Graph topology is isomorphic, but railway network graph differs (point is no point)"
                )
            if __node_a is None or __node_b is None:
                raise ValueError(
                    "Graph topology is isomorphic, but railway network graph differs (topology broken)"
                )
            open_nodes.append((__node_a, __node_b))

        def __add_edges_to_matching(__edge_a: Edge, __edge_b: Edge):
            if __edge_a in result.edge_matching.element_matching:
                if result.edge_matching.element_matching[__edge_a] != __edge_b:
                    raise ValueError(
                        "Graph topology is isomorphic, but railway network graph differs (edge graph broken)"
                    )
            else:
                result.edge_matching.element_matching[__edge_a] = __edge_b

        for node_a, node_b in given_node_matching.items():
            __add_to_open_nodes(node_a, node_b)

        # node and edge matching with a bfs
        while open_nodes:
            current_tuple = open_nodes.pop(0)
            node_a = current_tuple[0]
            node_b = current_tuple[1]
            if node_a in result.node_matching.element_matching:
                if result.node_matching.element_matching[node_a] != node_b:
                    raise ValueError(
                        "Graph topology is isomorphic, but railway network graph differs (connections at points)"
                    )
                continue
            else:
                result.node_matching.element_matching[node_a] = node_b

            __add_to_open_nodes(node_a.connected_on_head, node_b.connected_on_head)
            __add_edges_to_matching(node_a.connected_edge_on_head, node_b.connected_edge_on_head)
            if node_a.is_point():
                __add_to_open_nodes(node_a.connected_on_left, node_b.connected_on_left)
                __add_edges_to_matching(
                    node_a.connected_edge_on_left, node_b.connected_edge_on_left
                )
                __add_to_open_nodes(node_a.connected_on_right, node_b.connected_on_right)
                __add_edges_to_matching(
                    node_a.connected_edge_on_right, node_b.connected_edge_on_right
                )

        if not skip_signals:

            def __add_signal_lists_to_matching(
                signal_list_a: List[Signal], signal_list_b: List[Signal]
            ):
                for i in range(0, len(signal_list_a)):
                    signal_a = signal_list_a[i]
                    signal_b = signal_list_b[i]
                    result.signal_matching.element_matching[signal_a] = signal_b

            # signal matching
            for edge_a in topology_a.edges.values():
                edge_b = result.edge_matching.element_matching[edge_a]
                if not edge_a.signals and not edge_b.signals:
                    continue
                if not edge_a.signals or not edge_b.signals:
                    raise ValueError(
                        f"Signals on edges {edge_a.uuid} and {edge_b.uuid} does not match"
                    )
                in_direction_a = [
                    signal for signal in edge_a.signals if signal.direction == SignalDirection.IN
                ]
                in_direction_a.sort(key=lambda signal: signal.distance_edge)
                other_direction_a = [
                    signal for signal in edge_a.signals if signal.direction == SignalDirection.GEGEN
                ]
                other_direction_a.sort(key=lambda signal: signal.distance_edge)
                in_direction_b = [
                    signal for signal in edge_b.signals if signal.direction == SignalDirection.IN
                ]
                in_direction_b.sort(key=lambda signal: signal.distance_edge)
                other_direction_b = [
                    signal for signal in edge_b.signals if signal.direction == SignalDirection.GEGEN
                ]
                other_direction_b.sort(key=lambda signal: signal.distance_edge)

                if result.node_matching.element_matching[edge_a.node_a] != edge_b.node_a:
                    # edge b is reversed, so switch lists
                    in_direction_b, other_direction_b = list(reversed(other_direction_b)), list(
                        reversed(in_direction_b)
                    )

                if len(in_direction_a) != len(in_direction_b) or len(other_direction_a) != len(
                    other_direction_b
                ):
                    raise ValueError(
                        f"Number of signals on edges {edge_a.uuid} and {edge_b.uuid} differs (per direction)"
                    )
                __add_signal_lists_to_matching(in_direction_a, in_direction_b)
                __add_signal_lists_to_matching(other_direction_a, other_direction_b)

    @staticmethod
    def _are_topologies_isomorphic(topology_a: Topology, topology_b: Topology):
        if len(topology_a.nodes) != len(topology_b.nodes) or len(topology_a.edges) != len(
            topology_b.edges
        ):
            # Catch easy case before running expensive network x lib
            return False
        graph_a = topology_a.to_networkx_graph()
        graph_b = topology_b.to_networkx_graph()
        return nx.is_isomorphic(graph_a, graph_b)

    @staticmethod
    def _calc_distance_for_matching(
        matching: CompareMatching,
        exclude_ends_in_calculation,
        element_type: str = "node",
        start_node_a: Node = None,
        start_node_b: Node = None,
    ):
        if not matching.element_matching:
            return -1.0

        distance_sum: float = 0.0
        for element_a in matching.element_matching:
            element_b = matching.element_matching[element_a]

            if element_type == "node":
                if exclude_ends_in_calculation and not element_a.is_point():
                    continue
                start_geo_node_a = start_node_a.geo_node
                start_geo_node_b = start_node_b.geo_node
                geo_node_a: GeoNode = element_a.geo_node
                geo_node_b: GeoNode = element_b.geo_node
                distance = abs(
                    start_geo_node_a.get_distance_to_other_geo_node(geo_node_a)
                    - start_geo_node_b.get_distance_to_other_geo_node(geo_node_b)
                )
                print(f"From {element_a.uuid} to {element_b.uuid}: {distance}")
                distance_sum += distance
            elif element_type == "edge":
                if exclude_ends_in_calculation and (
                    not element_a.node_a.is_point() or not element_a.node_b.is_point()
                ):
                    continue
                print(
                    f"Edge {element_a.uuid} compared to {element_b.uuid}: {abs(element_a.length - element_b.length)}"
                )
                distance_sum += abs(element_a.length - element_b.length)
            elif element_type == "signal":
                x_a, y_a = element_a.get_calculated_coordinates()
                x_b, y_b = element_b.get_calculated_coordinates()
                distance_sum += DbrefGeoNode(x_a, y_a).get_distance_to_other_geo_node(
                    DbrefGeoNode(x_b, y_b)
                )

        return distance_sum
