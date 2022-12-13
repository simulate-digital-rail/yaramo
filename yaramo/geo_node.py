from abc import ABC, abstractmethod
from yaramo.base_element import BaseElement
from yaramo.geo_point import DbrefGeoPoint, Wgs84GeoPoint


class GeoNode(ABC, BaseElement):        

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def get_distance_to_other_geo_node(self, geo_node_b: 'GeoNode'):
        pass

class Wgs84GeoNode(GeoNode):

    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = Wgs84GeoPoint(x,y)

    def get_distance_to_other_geo_node(self, geo_node_b: 'Wgs84GeoNode'):
        return self.geo_point.get_distance_to_other_geo_point(geo_node_b.geo_point)

class DbrefGeoNode(GeoNode):

    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = DbrefGeoPoint(x,y)

    def get_distance_to_other_geo_node(self, geo_node_b: 'DbrefGeoNode'):
        return self.geo_point.get_distance_to_other_geo_point(geo_node_b.geo_point)

