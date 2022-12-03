import math

from yaramo.base_element import BaseElement
from yaramo.geo_point import GeoPoint


class GeoNode(BaseElement):

    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = GeoPoint(x,y)
    
    def get_distance_to_other_geo_node(self, geo_node_b):
        min_x = min(self.x, geo_node_b.x)
        min_y = min(self.y, geo_node_b.y)
        max_x = max(self.x, geo_node_b.x)
        max_y = max(self.y, geo_node_b.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))


