from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
import math

from yaramo.base_element import BaseElement

class GeoPoint(ABC, BaseElement):
    def __init__(
        self,
        x,
        y,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.x = x
        self.y = y

    @abstractmethod
    def get_distance_to_other_geo_point(self, geo_point_b: "GeoPoint"):
        pass

class Wgs84GeoPoint(GeoPoint):

    def get_distance_to_other_geo_point(self, geo_point_b: "Wgs84GeoPoint"):
        assert type(self) == type(geo_point_b), "You cannot calculate the distance between a Wgs84GeoPoint and a DbrefGeoPoint!"
        return self.__haversine_distance(geo_point_b)

    def __haversine_distance(self, geo_point_b: "GeoPoint"):
        pi_over_180 = Decimal(math.pi / 180)
        return (
            2
            * 6371000
            * math.asin(
                math.pi
                / 180
                * math.sqrt(
                    math.pow(math.sin((pi_over_180 * (geo_point_b.x - self.x)) / 2), 2)
                    + math.cos(pi_over_180 * self.x)
                    * math.cos(pi_over_180 * geo_point_b.x)
                    * math.pow(
                        math.sin((pi_over_180 * (geo_point_b.y - self.y)) / 2), 2
                    )
                )
            )
        )

class DbrefGeoPoint(GeoPoint):

    def get_distance_to_other_geo_point(self, geo_point_b: "DbrefGeoPoint"):
        assert type(self) == type(geo_point_b), "You cannot calculate the distance between a DbrefGeoPoint and a Wgs84GeoPoint!"
        return self.__eucldian_distance(geo_point_b)

    def __eucldian_distance(self, geo_point_b: "GeoPoint"):
        min_x = min(self.x, geo_point_b.x)
        min_y = min(self.y, geo_point_b.y)
        max_x = max(self.x, geo_point_b.x)
        max_y = max(self.y, geo_point_b.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))
