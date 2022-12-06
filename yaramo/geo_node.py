from decimal import Decimal
from enum import Enum
import math

from yaramo.base_element import BaseElement
from yaramo.geo_point import GeoPoint

class DistanceFunction(Enum):
    Euclidean = 0
    Haversine = 1 

class GeoNode(BaseElement):        

    def __init__(self, x, y, distance_function: DistanceFunction=None, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = GeoPoint(x,y)
        self.distance_function = distance_function or DistanceFunction.Euclidean

    def __eucldian_distance(self, geo_node_b: 'GeoNode'):
        min_x = min(self.geo_point.x, geo_node_b.geo_point.x)
        min_y = min(self.geo_point.y, geo_node_b.geo_point.y)
        max_x = max(self.geo_point.x, geo_node_b.geo_point.x)
        max_y = max(self.geo_point.y, geo_node_b.geo_point.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))
    
    def __haversine_distance(self, geo_node_b: 'GeoNode'):
        pi_over_180  = Decimal(math.pi/180)
        return 2 * 6371000 * math.asin(
            math.pi/180*math.sqrt(
                math.pow(math.sin((pi_over_180*(geo_node_b.geo_point.x - self.geo_point.x))/2),2)+
                math.cos(pi_over_180*self.geo_point.x)*
                math.cos(pi_over_180*geo_node_b.geo_point.x)*
                math.pow(math.sin((pi_over_180*(geo_node_b.geo_point.y - self.geo_point.y))/2),2)
            )
        )

    def get_distance_to_other_geo_node(self, geo_node_b: 'GeoNode'):
        match self.distance_function:
            case DistanceFunction.Euclidean:
                return self.__eucldian_distance(geo_node_b)
            case DistanceFunction.Haversine:
                return self.__haversine_distance(geo_node_b)



