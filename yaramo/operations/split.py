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
        split_edges: Dict[Edge, float],
        add_missing_elements_to_topology: None | Label = None,
    ) -> Tuple[Topology, Topology]:
        Split._validate_split_edges(split_edges)

        topology_a = Topology()
        OperationsHelper.copy_topology_metadata(topology, topology_a)
        topology_b = Topology()
        OperationsHelper.copy_topology_metadata(topology, topology_b)

        new_end_nodes = Split._split_edges(topology, split_edges)
        node_labels, edge_labels, signal_labels = Split._label_elements(topology, new_end_nodes)

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

        # Assign routes
        for route in topology.routes.values():
            start_signal_label = signal_labels[route.start_signal]
            end_signal_label = signal_labels[route.end_signal]
            if start_signal_label != end_signal_label:
                # Route goes over split edges, remove this route
                continue
            if start_signal_label == Label.A_Topology:
                topology_a.add_route(route)
            elif start_signal_label == Label.B_Topology:
                topology_b.add_route(route)

        Split._validate_for_data_loss(topology, topology_a, topology_b, split_edges)

        return topology_a, topology_b

    @staticmethod
    def _validate_split_edges(split_edges: Dict[Edge, float]):
        for edge, distance_on_edge in split_edges.items():
            edge.update_length()
            if edge.length < distance_on_edge:
                raise ValueError(f"The edge {edge.name} is shorter than split distance.")
            if distance_on_edge <= 0:
                raise ValueError(f"The split distance of the edge {edge.name} has to be greater than 0.")
            for signal in edge.signals:
                if signal.distance_edge == distance_on_edge:
                    raise ValueError(
                        f"The edge {edge.name} contains a signal exactly at the position, where it "
                        f"should be split. This is not possible."
                    )

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

            new_end_nodes[edge] = (end_node_a, end_node_b)

        return new_end_nodes

    @staticmethod
    def _label_elements(
        topology: Topology, new_end_nodes: Dict[Edge, Tuple[Node, Node]]
    ) -> Tuple[Dict[Node, Label], Dict[Edge, Label], Dict[Signal, Label]]:
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

        if not new_end_nodes:
            raise ValueError("No new end nodes found. Split not possible")

        for end_node_pair in new_end_nodes.values():
            node_a = end_node_pair[0]
            node_b = end_node_pair[1]
            if node_a not in node_labels and node_b not in node_labels:
                _dfs(node_a, Label.A_Topology)
                _dfs(node_b, Label.B_Topology)
            elif node_a in node_labels and node_b in node_labels:
                if node_labels[node_a] == node_labels[node_b]:
                    raise ValueError("Split edges do not fully split. Split not possible.")
            elif node_a in node_labels:
                _dfs(node_b, Label.get_opposite_label(node_labels[node_a]))
            elif node_b in node_labels:
                _dfs(node_a, Label.get_opposite_label(node_labels[node_b]))

        return node_labels, edge_labels, signal_labels

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
        for node_uuid in topology.nodes:
            if node_uuid not in topology_a.nodes and node_uuid not in topology_b.nodes:
                raise ValueError(
                    "Data loss (lost node). Split edges split topology in more than two splits. Not supported."
                )

        for edge_uuid, edge in topology.edges.items():
            if edge in split_edges.keys():
                continue
            if edge_uuid not in topology_a.edges and edge_uuid not in topology_b.edges:
                raise ValueError(
                    "Data loss (lost edge). Split edges split topology in more than two splits. Not supported."
                )

        for signal_uuid in topology.signals:
            if signal_uuid not in topology_a.signals and signal_uuid not in topology_b.signals:
                raise ValueError(
                    "Data loss (lost signal). Split edges split topology in more than two splits. Not supported."
                )
