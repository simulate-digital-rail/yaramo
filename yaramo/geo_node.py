from yaramo.base_element import BaseElement
from yaramo.geo_point import DistanceFunction, GeoPoint


class GeoNode(BaseElement):        

    def __init__(self, x, y, distance_function: DistanceFunction=None, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = GeoPoint(x,y)
        self.distance_function = distance_function or DistanceFunction.Euclidean


    def get_distance_to_other_geo_node(self, geo_node_b: 'GeoNode'):
        return self.geo_point.get_distance_to_other_geo_point(geo_node_b.geo_point)




