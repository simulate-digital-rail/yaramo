from ..model import Topology, Node
from typing import Dict


class Union:

    @staticmethod
    def union(topology_a: Topology, topology_b: Topology, node_matching: Dict[Node, Node]) -> Topology:
        return topology_a
