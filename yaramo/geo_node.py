import math
from abc import ABC, abstractmethod

import pyproj

from yaramo.base_element import BaseElement


class GeoNode(ABC, BaseElement):
    """This is the baseclass of specific GeoNodes that use different coordinate systems.

    A GeoNode is characterized by it's x and y coordinates.
    """

    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y

    @abstractmethod
    def get_distance_to_other_geo_node(self, geo_node_b: "GeoNode"):
        pass

    def to_serializable(self):
        return self.__dict__, {}

    @abstractmethod
    def to_wgs84(self):
        pass

    @abstractmethod
    def to_dbref(self):
        pass


class Wgs84GeoNode(GeoNode):
    def get_distance_to_other_geo_node(self, geo_node_b: "Wgs84GeoNode"):
        assert type(self) == type(
            geo_node_b
        ), "You cannot calculate the distance between a Wgs84GeoNode and a DbrefGeoNode!"
        return self.__haversine_distance(geo_node_b) / 1000

    def __haversine_distance(self, geo_node_b: "GeoNode"):
        pi_over_180 = float(math.pi / 180)
        return (
            2
            * 6371000
            * math.asin(
                math.pi
                / 180
                * math.sqrt(
                    math.pow(math.sin((pi_over_180 * (geo_node_b.x - self.x)) / 2), 2)
                    + math.cos(pi_over_180 * self.x)
                    * math.cos(pi_over_180 * geo_node_b.x)
                    * math.pow(math.sin((pi_over_180 * (geo_node_b.y - self.y)) / 2), 2)
                )
            )
        )

    def to_wgs84(self):
        return self

    def to_dbref(self):
        transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:31468")
        x, y = transformer.transform(self.y, self.x)
        return DbrefGeoNode(x, y)


class DbrefGeoNode(GeoNode):
    def get_distance_to_other_geo_node(self, geo_node_b: "DbrefGeoNode"):
        assert type(self) == type(
            geo_node_b
        ), "You cannot calculate the distance between a DbrefGeoNode and a Wgs84GeoNode!"
        return self.__eucldian_distance(geo_node_b)

    def __eucldian_distance(self, geo_node_b: "GeoNode"):
        min_x = min(self.x, geo_node_b.x)
        min_y = min(self.y, geo_node_b.y)
        max_x = max(self.x, geo_node_b.x)
        max_y = max(self.y, geo_node_b.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))

    def to_wgs84(self):
        raise NotImplementedError

    def to_dbref(self):
        return self
