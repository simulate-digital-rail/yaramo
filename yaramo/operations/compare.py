from enum import Enum, auto
from typing import Dict, List, Set, Tuple

from ..model import DbrefGeoNode, Edge, GeoNode, Node, Signal, Topology, Wgs84GeoNode


class CompareResult:
    def __init__(self):
        self.comparability_degree: float = -1.0
        self.node_matching: Dict[Node, Node] = {}
        self.edge_matching: Dict[Edge, Edge] = {}
        self.signal_matching: Dict[Signal, Signal] = {}


class CompareMode(Enum):
    EXACT = auto()
    EXACT_BUT_IDS = auto()
    ISOMORPHIC = auto()


class Compare:
    @staticmethod
    def compare(
        topology_a: Topology,
        topology_b: Topology,
        compare_mode: CompareMode,
        id_matching: Dict[str, str] | None = None,
    ) -> CompareResult:
        if id_matching is None:
            id_matching = {}
        return CompareResult()
