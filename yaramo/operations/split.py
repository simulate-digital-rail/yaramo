from typing import Dict, Tuple

from ..model import Edge, Topology


class Split:
    @staticmethod
    def split(topology: Topology, split_edges: Dict[Edge, float]) -> Tuple[Topology, Topology]:
        return topology, topology
