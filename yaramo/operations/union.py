from typing import Dict, List

from ..model import Edge, Node, SignalDirection, Topology
from .operationshelper import OperationsHelper


class Union:
    @staticmethod
    def union(
        topology_a: Topology, node_matching: Dict[Node, Node], topology_b: Topology = None
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

        topology_ab = Topology()
        OperationsHelper.copy_topology_metadata(topology_a, topology_ab)

        topology_ab.nodes.update(topology_a.nodes)
        topology_ab.nodes.update(topology_b.nodes)
        topology_ab.edges.update(topology_a.edges)
        topology_ab.edges.update(topology_b.edges)
        topology_ab.signals.update(topology_a.signals)
        topology_ab.signals.update(topology_b.signals)
        topology_ab.routes.update(topology_a.routes)
        topology_ab.routes.update(topology_b.routes)
        topology_ab.vacancy_sections.update(topology_a.vacancy_sections)
        topology_ab.vacancy_sections.update(topology_b.vacancy_sections)

        for node_a, node_b in node_matching.items():
            union_edge_a: Edge = node_a.connected_edges[0]
            union_edge_a_direction_in = union_edge_a.node_b == node_a  # From Point to End
            union_edge_b: Edge = node_b.connected_edges[0]
            union_edge_b_direction_in = union_edge_b.node_b == node_b  # From Point to End
            other_node_a: Node = union_edge_a.get_opposite_node(node_a)
            other_node_b: Node = union_edge_b.get_opposite_node(node_b)

            # create new edge
            union_edge_ab = Edge(other_node_a, other_node_b)
            other_node_a.remove_edge(union_edge_a)
            other_node_b.remove_edge(union_edge_b)
            Union._connect_edge_at_old_position(other_node_a, union_edge_ab)
            Union._connect_edge_at_old_position(other_node_b, union_edge_ab)

            # add geo nodes
            if union_edge_a_direction_in:
                union_edge_ab.intermediate_geo_nodes.extend(union_edge_a.intermediate_geo_nodes)
            else:
                union_edge_ab.intermediate_geo_nodes.extend(
                    reversed(union_edge_a.intermediate_geo_nodes)
                )
            union_edge_ab.intermediate_geo_nodes.append(node_a.geo_node)
            union_edge_ab.intermediate_geo_nodes.append(node_b.geo_node)
            if not union_edge_b_direction_in:
                union_edge_ab.intermediate_geo_nodes.extend(union_edge_b.intermediate_geo_nodes)
            else:
                union_edge_ab.intermediate_geo_nodes.extend(
                    reversed(union_edge_b.intermediate_geo_nodes)
                )

            # add signals and max speed
            union_edge_ab.maximum_speed = Union._get_maximum_speed(union_edge_a, union_edge_b)
            if union_edge_a.signals or union_edge_b.signals:
                union_edge_a.update_length()
                union_edge_b.update_length()
                if union_edge_a.signals:
                    Union._union_signals_of_edge(
                        union_edge_a, union_edge_a_direction_in, 0.0, union_edge_ab
                    )
                if union_edge_b.signals:
                    Union._union_signals_of_edge(
                        union_edge_b,
                        union_edge_b_direction_in,
                        union_edge_a.length
                        + (node_a.geo_node.get_distance_to_other_geo_node(node_b.geo_node)),
                        union_edge_ab,
                    )

            # remove old edges and split nodes
            topology_ab.nodes.pop(node_a.uuid)
            topology_ab.nodes.pop(node_b.uuid)
            topology_ab.edges.pop(union_edge_a.uuid)
            topology_ab.edges.pop(union_edge_b.uuid)

            # add new edge
            topology_ab.add_edge(union_edge_ab)

            pass

        return topology_ab

    @staticmethod
    def _get_maximum_speed(_union_edge_a: Edge, _union_edge_b: Edge) -> int | None:
        if _union_edge_a.maximum_speed is None and _union_edge_b.maximum_speed is None:
            return None
        if _union_edge_a.maximum_speed is not None and _union_edge_b.maximum_speed is not None:
            return min(_union_edge_a.maximum_speed, _union_edge_b.maximum_speed)
        if _union_edge_a.maximum_speed is not None:
            return _union_edge_a.maximum_speed
        return _union_edge_b.maximum_speed

    @staticmethod
    def _union_signals_of_edge(
        _edge: Edge, _edge_direction_in: bool, _distance_offset: float, _union_edge_ab: Edge
    ):
        for signal in _edge.signals:
            # distance_edge and direction
            if _edge_direction_in:
                signal.distance_edge = float(signal.distance_edge) + _distance_offset
            else:
                signal.distance_edge = (_edge.length - signal.distance_edge) + _distance_offset
                signal.direction = SignalDirection.get_other_direction(signal.direction)

            signal.edge = _union_edge_ab
            _union_edge_ab.signals.append(signal)

    @staticmethod
    def _connect_edge_at_old_position(_node: Node, _edge: Edge):
        if _node.connected_edge_on_head is None:
            _node.set_connection_head_edge(_edge)
        elif _node.connected_edge_on_left is None:
            _node.set_connection_left_edge(_edge)
        elif _node.connected_edge_on_right is None:
            _node.set_connection_right_edge(_edge)

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
