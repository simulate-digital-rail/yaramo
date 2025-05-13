from yaramo.model import DbrefGeoNode, EuclideanGeoNode, GeoNode, Topology, Wgs84GeoNode


class OperationsHelper:
    @staticmethod
    def copy_topology_metadata(orig_topology: Topology, new_topology: Topology):
        new_topology.name = orig_topology.name
        new_topology.current_status = orig_topology.current_status
        new_topology.status_information = orig_topology.status_information
        new_topology.created_at = orig_topology.created_at
        new_topology.created_with = orig_topology.created_with
