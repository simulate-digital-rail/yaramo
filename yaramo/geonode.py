import math
import uuid


class GeoNode(object):

    def __init__(self, x, y, uuid: str = None):
        self.x = x
        self.y = y
        self.uuid = uuid or str(uuid.uuid4())
    
    def get_distance_to_other_geo_node(self, geo_node_b):
        min_x = min(self.x, geo_node_b.x)
        min_y = min(self.y, geo_node_b.y)
        max_x = max(self.x, geo_node_b.x)
        max_y = max(self.y, geo_node_b.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))


