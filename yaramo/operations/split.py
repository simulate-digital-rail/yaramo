from ..model import Topology, Edge
from typing import List, Tuple


class Split:

    @staticmethod
    def split(topology: Topology, split_edges: List[Edge]) -> Tuple[Topology, Topology]:
        return topology, topology
