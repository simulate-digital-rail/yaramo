from enum import Enum, auto
from typing import Dict, List, Set, Tuple

from ..model import DbrefGeoNode, Edge, GeoNode, Node, Signal, Topology, Wgs84GeoNode
from .operationshelper import OperationsHelper


class Label(Enum):
    A_Topology = auto()
    B_Topology = auto()

    @staticmethod
    def get_opposite_label(label):
        if label == Label.A_Topology:
            return Label.B_Topology
        return Label.A_Topology


class Split:
    @staticmethod
    def split(
        topology: Topology,
        split_edges: None | Dict[Edge, float] = None,
        add_missing_elements_to_topology: None | Label = None,
        node_label_assignments: Node | Dict[Node, Label] = None,
    ) -> Tuple[Topology, Topology, Dict[Edge, Tuple[Node, Node]]]:
        if not topology.nodes:
            raise ValueError("Given topology is empty.")
        if split_edges is None:
            split_edges = {}
        else:
            Split._validate_split_edges(topology, split_edges)
        if node_label_assignments is None:
            node_label_assignments = {}
        else:
            Split._validate_node_label_assignment(topology, node_label_assignments)

        if not split_edges and not node_label_assignments:
            raise ValueError("Either split edges or node label assignments are necessary")

        topology_a = Topology()
        OperationsHelper.copy_topology_metadata(topology, topology_a)
        topology_b = Topology()
        OperationsHelper.copy_topology_metadata(topology, topology_b)

        new_end_nodes = {}
        if split_edges:
            new_end_nodes = Split._split_edges(topology, split_edges)

        node_labels, edge_labels, signal_labels = Split._label_elements(
            topology, new_end_nodes, node_label_assignments
        )

        if add_missing_elements_to_topology is not None:
            Split._assign_missing_elements_to_label(
                topology, node_labels, edge_labels, signal_labels, add_missing_elements_to_topology
            )

        # Add nodes, edges and signals to destination topologies.
        def _add_elements_to_topology(
            _element_label_matching, _topology_a_method, _topology_b_method
        ):
            for _element, _label in _element_label_matching.items():
                if _label == Label.A_Topology:
                    _topology_a_method(_element)
                elif _label == Label.B_Topology:
                    _topology_b_method(_element)

        _add_elements_to_topology(node_labels, topology_a.add_node, topology_b.add_node)
        _add_elements_to_topology(edge_labels, topology_a.add_edge, topology_b.add_edge)
        _add_elements_to_topology(signal_labels, topology_a.add_signal, topology_b.add_signal)
        Split._assign_routes_to_topologies(
            topology, topology_a, topology_b, edge_labels, signal_labels
        )

        Split._validate_for_data_loss(topology, topology_a, topology_b, split_edges)

        # Ensure first element of new end nodes is always in A-topology
        for edge, new_end_node_pair in new_end_nodes.items():
            if node_labels[new_end_node_pair[0]] == Label.B_Topology:
                new_end_nodes[edge] = (new_end_node_pair[1], new_end_node_pair[0])

        return topology_a, topology_b, new_end_nodes

    @staticmethod
    def _validate_split_edges(topology: Topology, split_edges: Dict[Edge, float]):
        for edge, distance_on_edge in split_edges.items():
            if edge not in topology:
                raise ValueError("Given split edge is not part of the topology")
            edge.update_length()
            if edge.length < distance_on_edge:
                raise ValueError(f"The edge {edge.name} is shorter than split distance.")
            if distance_on_edge <= 0:
                raise ValueError(
                    f"The split distance of the edge {edge.name} has to be greater than 0."
                )
            for signal in edge.signals:
                if signal.distance_edge == distance_on_edge:
                    raise ValueError(
                        f"The edge {edge.name} contains a signal exactly at the position, where it "
                        f"should be split. This is not possible."
                    )

    @staticmethod
    def _validate_node_label_assignment(
        topology: Topology, node_label_assignment: Dict[Node, Label]
    ):
        for node in node_label_assignment:
            if node not in topology:
                raise ValueError("Node of node label assignment not in topology.")

    @staticmethod
    def _split_edges(
        topology: Topology, split_edges: Dict[Edge, float]
    ) -> Dict[Edge, Tuple[Node, Node]]:
        def _connect_edge_at_old_position(_node: Node, _edge: Edge):
            if _node.connected_edge_on_head is None:
                _node.set_connection_head_edge(_edge)
            elif _node.connected_edge_on_left is None:
                _node.set_connection_left_edge(_edge)
            elif _node.connected_edge_on_right is None:
                _node.set_connection_right_edge(_edge)

        def _get_new_geo_node_same_type(_old_geo_node: GeoNode, x: float, y: float) -> GeoNode:
            if isinstance(_old_geo_node, Wgs84GeoNode):
                return Wgs84GeoNode(x, y)
            elif isinstance(_old_geo_node, DbrefGeoNode):
                return DbrefGeoNode(x, y)
            raise NotImplementedError

        new_end_nodes: Dict[Edge, Tuple[Node, Node]] = {}
        for edge, distance_on_edge in split_edges.items():
            # Get coordinates of new edge nodes and separate geo nodes
            x, y = edge.get_coordinates_on_edge_by_distance_from_start_node(distance_on_edge)
            geo_nodes_a = []
            geo_nodes_b = []
            if edge.intermediate_geo_nodes:
                distance_so_far = 0.0
                last_geo_node = edge.node_a.geo_node
                for inter_geo_node in edge.intermediate_geo_nodes:
                    cur_distance = last_geo_node.get_distance_to_other_geo_node(inter_geo_node)
                    distance_so_far += cur_distance
                    if distance_so_far < distance_on_edge:
                        geo_nodes_a.append(inter_geo_node)
                    elif distance_so_far > distance_on_edge:
                        geo_nodes_b.append(inter_geo_node)
                    # else (=): discard intermediate geo node, since the new end node is at that position.
                    last_geo_node = inter_geo_node

            # Split edge
            node_a = edge.node_a
            node_a.remove_edge(edge)
            end_node_a = Node(geo_node=_get_new_geo_node_same_type(node_a.geo_node, x, y))
            edge_a = Edge(node_a, end_node_a)
            edge_a.intermediate_geo_nodes = geo_nodes_a
            _connect_edge_at_old_position(node_a, edge_a)
            end_node_a.set_connection_head_edge(edge_a)
            topology.add_node(end_node_a)
            topology.add_edge(edge_a)

            node_b = edge.node_b
            node_b.remove_edge(edge)
            end_node_b = Node(geo_node=_get_new_geo_node_same_type(node_b.geo_node, x, y))
            edge_b = Edge(end_node_b, node_b)
            edge_b.intermediate_geo_nodes = geo_nodes_b
            _connect_edge_at_old_position(node_b, edge_b)
            end_node_b.set_connection_head_edge(edge_b)
            topology.add_node(end_node_b)
            topology.add_edge(edge_b)

            for signal in edge.signals:
                if signal.distance_edge < distance_on_edge:
                    edge_a.signals.append(signal)
                    signal.edge = edge_a
                else:
                    edge_b.signals.append(signal)
                    signal.edge = edge_b

            for route in topology.routes.values():
                if edge in route.edges:
                    route.edges.remove(edge)
                    if (
                        route.start_signal.edge not in route.edges
                        or route.end_signal.edge not in route.edges
                    ):
                        if route.start_signal.edge not in route.edges:
                            route.edges.add(route.start_signal.edge)
                        if route.end_signal.edge not in route.edges:
                            route.edges.add(route.end_signal.edge)
                    else:
                        route.edges.add(edge_a)
                        route.edges.add(edge_b)

            new_end_nodes[edge] = (end_node_a, end_node_b)

        return new_end_nodes

    @staticmethod
    def _label_elements(
        topology: Topology,
        new_end_nodes: Dict[Edge, Tuple[Node, Node]],
        node_label_assignments: Dict[Node, Label],
    ) -> Tuple[Dict[Node, Label], Dict[Edge, Label], Dict[Signal, Label]]:
        if not new_end_nodes and not node_label_assignments:
            raise ValueError("No end nodes but also nothing labeled. Split not possible")

        node_labels: Dict[Node, Label] = {}
        edge_labels: Dict[Edge, Label] = {}
        signal_labels: Dict[Signal, Label] = {}

        def _set_label(_element, _label, _mapping):
            if _element in _mapping and _mapping[_element] != _label:
                raise ValueError("Split edges do not fully split. Split not possible.")
            _mapping[_element] = _label

        def _dfs(_start_node: Node, _label):
            node_list: List[Node] = [_start_node]
            visited: Set[Node] = set()
            while node_list:
                cur_node: Node = node_list.pop()
                if cur_node in visited:
                    continue
                _set_label(cur_node, _label, node_labels)
                for edge in cur_node.connected_edges:
                    _set_label(edge, _label, edge_labels)
                    for signal in edge.signals:
                        _set_label(signal, _label, signal_labels)

                node_list.extend(cur_node.connected_nodes)
                visited.add(cur_node)

        def _get_any_unlabeled_end_node_pair():
            for pair in new_end_nodes.values():
                if pair[0] not in node_labels and pair[1] not in node_labels:
                    return pair
            return None

        def _get_next_end_node_pair():
            for pair in new_end_nodes.values():
                _node_a = pair[0]
                _node_b = pair[1]
                if (_node_a in node_labels and _node_b not in node_labels) or (
                    _node_a not in node_labels and _node_b in node_labels
                ):
                    return pair
            return _get_any_unlabeled_end_node_pair()

        if node_label_assignments:
            for node, label in node_label_assignments.items():
                _dfs(node, label)
        else:
            # Nothing labeled so far, start with any pair
            any_end_node_pair = _get_any_unlabeled_end_node_pair()
            _dfs(any_end_node_pair[0], Label.A_Topology)
            _dfs(any_end_node_pair[1], Label.B_Topology)

        next_pair = _get_next_end_node_pair()
        while next_pair is not None:
            node_a = next_pair[0]
            node_b = next_pair[1]
            if node_a not in node_labels and node_b not in node_labels:
                _dfs(node_a, Label.A_Topology)
                _dfs(node_b, Label.B_Topology)
            elif node_a in node_labels and node_b in node_labels:
                if node_labels[node_a] == node_labels[node_b]:
                    raise ValueError(
                        "Split edges do not fully split or is not colorable with two colors. Split not possible."
                    )
            elif node_a in node_labels:
                _dfs(node_b, Label.get_opposite_label(node_labels[node_a]))
            elif node_b in node_labels:
                _dfs(node_a, Label.get_opposite_label(node_labels[node_b]))
            next_pair = _get_next_end_node_pair()

        # Verify all end node pairs have different labels
        for pair in new_end_nodes.values():
            node_a = pair[0]
            node_b = pair[1]
            if node_labels[node_a] == node_labels[node_b]:
                raise ValueError(
                    "Split edges do not fully split or is not colorable with two colors. Split not possible."
                )

        return node_labels, edge_labels, signal_labels

    @staticmethod
    def _assign_routes_to_topologies(
        topology: Topology,
        topology_a: Topology,
        topology_b: Topology,
        edge_labels: Dict[Edge, Label],
        signal_labels: Dict[Signal, Label],
    ):
        for route in topology.routes.values():
            start_signal_label = signal_labels[route.start_signal]
            end_signal_label = signal_labels[route.end_signal]
            if start_signal_label != end_signal_label:
                # Route start and end in different areas, remove route
                continue
            all_edges_in_same_topology = True
            for edge in route.edges:
                if edge_labels[edge] != start_signal_label:
                    # Route goes over different area, remove route
                    all_edges_in_same_topology = False
            if not all_edges_in_same_topology:
                continue
            if start_signal_label == Label.A_Topology:
                topology_a.add_route(route)
            else:
                topology_b.add_route(route)

    @staticmethod
    def _assign_missing_elements_to_label(
        topology: Topology,
        node_labels: Dict[Node, Label],
        edge_labels: Dict[Edge, Label],
        signal_labels: Dict[Signal, Label],
        label: Label,
    ):
        for node in topology.nodes.values():
            if node not in node_labels:
                node_labels[node] = label
        for edge in topology.edges.values():
            if edge not in edge_labels:
                edge_labels[edge] = label
        for signal in topology.signals.values():
            if signal not in signal_labels:
                signal_labels[signal] = label

    @staticmethod
    def _validate_for_data_loss(
        topology: Topology,
        topology_a: Topology,
        topology_b: Topology,
        split_edges: Dict[Edge, float],
    ):
        for node in topology.nodes.values():
            if node not in topology_a and node not in topology_b:
                raise ValueError("Unexpected data loss (lost node).")

        for edge in topology.edges.values():
            if edge in split_edges:
                continue
            if edge not in topology_a and edge not in topology_b:
                raise ValueError("Unexpected data loss (lost edge).")

        for signal in topology.signals.values():
            if signal not in topology_a and signal not in topology_b:
                raise ValueError("Unexpected data loss (lost signal).")
