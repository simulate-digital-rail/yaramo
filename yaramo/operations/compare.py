from enum import Enum, auto
from typing import Dict, List, Set, Tuple

import networkx as nx

from ..model import DbrefGeoNode, Edge, GeoNode, Node, Signal, Topology, Wgs84GeoNode


class CompareMatching:

    def __init__(self):
        self.element_matching = {}
        self.not_found_in_a = []
        self.not_found_in_b = []


class CompareResult:
    def __init__(self):
        self.node_distance: float = -1.0
        self.node_matching: CompareMatching = CompareMatching()
        self.edge_matching: CompareMatching = CompareMatching()
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
                raise ValueError("For isomorphic topologies, at least one mathing node needs to be given.")

            # bfs at start nodes to generate matching

        result.node_distance = Compare._calc_distance_for_matching(result.node_matching)
        return result

    @staticmethod
    def _calc_exact_matching(result: CompareResult, topology_a: Topology, topology_b: Topology):
        Compare._calc_exact_element_matching(result.node_matching, topology_a.nodes, topology_b.nodes)
        Compare._calc_exact_element_matching(result.edge_matching, topology_a.edges, topology_b.edges)
        Compare._calc_exact_element_matching(result.signal_matching, topology_a.signals, topology_b.signals)

    @staticmethod
    def _calc_exact_element_matching(compare_matching: CompareMatching, element_dict_a: Dict, element_dict_b: Dict):
        for element_uuid_a, element_a in element_dict_a.items():
            if element_uuid_a in element_dict_b:
                compare_matching.element_matching[element_a] = element_dict_b[element_uuid_a]
            else:
                compare_matching.not_found_in_b.append(element_a)
        for element_uuid_b in (element_dict_b.keys() - element_dict_a.keys()):
            compare_matching.not_found_in_a.append(element_dict_b[element_uuid_b])

    @staticmethod
    def _are_topologies_isomorphic(topology_a: Topology, topology_b: Topology):
        if len(topology_a.nodes) != len(topology_b.nodes) or len(topology_a.edges) != len(topology_b.edges):
            # Catch easy case before running expensive network x lib
            return False
        graph_a = topology_a.to_networkx_graph()
        graph_b = topology_b.to_networkx_graph()
        return nx.is_isomorphic(graph_a, graph_b)

    @staticmethod
    def _calc_distance_for_matching(matching: CompareMatching, element_type: str = "node"):
        if not matching.element_matching:
            return -1.0
        distance_sum: float = 0.0
        for element_a in matching.element_matching:
            element_b = matching.element_matching[element_a]
            if element_type == "node":
                geo_node_a: GeoNode = element_a.geo_node
                geo_node_b: GeoNode = element_b.geo_node
                distance_sum += geo_node_a.get_distance_to_other_geo_node(geo_node_b)
            elif element_type == "edge":
                raise NotImplementedError()
            elif element_type == "signal":
                raise NotImplementedError()
        return distance_sum

