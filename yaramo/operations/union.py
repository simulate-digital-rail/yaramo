from typing import Dict, List

from ..model import Node, Topology


class Union:
    @staticmethod
    def union(
        topology_a: Topology, topology_b: Topology, node_matching: Dict[Node, Node]
    ) -> Topology:
        if not (
            Union._are_all_nodes_in_topology(topology_a, node_matching.keys())
            and Union._are_all_nodes_in_topology(topology_b, node_matching.values())
        ):
            raise ValueError(
                "The node matching contains nodes, that are not inside the corresponding topology. Abort."
            )

        if not Union._are_all_nodes_ends(node_matching):
            raise ValueError(
                "Some of the nodes in the matching are points. All nodes have to be ends. Abort."
            )

        return topology_a

    @staticmethod
    def _are_all_nodes_in_topology(topology: Topology, node_list: [Node]) -> bool:
        for node in node_list:
            if node not in topology.nodes.values():
                return False
        return True

    @staticmethod
    def _are_all_nodes_ends(node_matching: Dict[Node, Node]) -> bool:
        for node_a in node_matching:
            if node_a.is_point() or node_matching[node_a].is_point():
                return False
        return True
