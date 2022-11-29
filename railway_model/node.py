from railway_model.geonode import GeoNode


class Node(object):
    uuid: str
    geo_node: GeoNode
    connected_nodes = list

    def __init__(self, uuid):
        self.uuid = uuid
        self.connected_on_head = None
        self.connected_on_left = None
        self.connected_on_right = None
        self.connected_nodes = []
        self.geo_node = None

    def set_connection_head(self, node: 'Node'):
        self.connected_on_head = node
        self.connected_nodes.append(node)

    def set_connection_left(self, node):
        self.connected_on_left = node
        self.connected_nodes.append(node)

    def set_connection_right(self, node):
        self.connected_on_right = node
        self.connected_nodes.append(node)

    def get_possible_followers(self, source):
        if source is None:
            return self.connected_nodes

        if len(self.connected_nodes) == 1:  
            return []

        if source.uuid == self.connected_on_head.uuid: 
            return [self.connected_on_left, self.connected_on_right]
        else:
            return [self.connected_on_head]
