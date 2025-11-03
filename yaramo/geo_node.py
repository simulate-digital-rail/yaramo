from __future__ import annotations

import math
from abc import ABC, abstractmethod

from haversine import Unit, haversine

from yaramo.base_element import BaseElement

from .utils.coordinateconversion import transform_dbref_to_wgs84, transform_wgs84_to_dbref


class GeoNode(ABC, BaseElement):
    """This is the baseclass of specific GeoNodes that use different coordinate systems.

    A GeoNode is characterized by it's x and y coordinates.
    """

    def __init__(self, x, y, data_source: str = "unknown", dbref_crs: str = "ER0", **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.data_source = data_source
        self.dbref_crs = dbref_crs

    @abstractmethod
    def get_distance_to_other_geo_node(self, geo_node_b: GeoNode):
        """Returns to distance to the given other GeoNode."""
        pass

    @abstractmethod
    def to_wgs84(self) -> Wgs84GeoNode:
        pass

    @abstractmethod
    def to_dbref(self) -> DbrefGeoNode:
        pass

    @abstractmethod
    def to_euclidean(self) -> EuclideanGeoNode:
        pass

    def to_serializable(self):
        return self.__dict__, {}

    @staticmethod
    def get_new_geo_node_same_type(old_geo_node: GeoNode, x: float, y: float) -> GeoNode:
        if isinstance(old_geo_node, Wgs84GeoNode):
            return Wgs84GeoNode(x, y)
        elif isinstance(old_geo_node, DbrefGeoNode):
            return DbrefGeoNode(x, y)
        elif isinstance(old_geo_node, EuclideanGeoNode):
            return EuclideanGeoNode(x, y)
        raise NotImplementedError


class Wgs84GeoNode(GeoNode):
    def get_distance_to_other_geo_node(self, geo_node_b: GeoNode):
        geo_node_b = geo_node_b.to_wgs84()
        return self.__haversine_distance(geo_node_b)

    def __haversine_distance(self, geo_node_b: GeoNode):
        own = (self.x, self.y)
        other = (geo_node_b.x, geo_node_b.y)
        return haversine(own, other, unit=Unit.METERS)

    def to_wgs84(self) -> Wgs84GeoNode:
        return self

    def to_dbref(self) -> DbrefGeoNode:
        x, y = transform_wgs84_to_dbref(self.x, self.y, self.dbref_crs)
        return DbrefGeoNode(x, y, self.data_source, self.dbref_crs, uuid=self.uuid)

    def to_euclidean(self) -> EuclideanGeoNode:
        return self.to_dbref().to_euclidean()


class DbrefGeoNode(GeoNode):
    def get_distance_to_other_geo_node(self, geo_node_b: GeoNode):
        # Separate DB Ref distance method not implemented yet, therefore use WGS84 distance
        return self.to_wgs84().get_distance_to_other_geo_node(geo_node_b)

    def to_wgs84(self) -> Wgs84GeoNode:
        x, y = transform_dbref_to_wgs84(self.x, self.y, self.dbref_crs)
        return Wgs84GeoNode(x, y, self.data_source, self.dbref_crs, uuid=self.uuid)

    def to_dbref(self) -> DbrefGeoNode:
        return self

    def to_euclidean(self) -> EuclideanGeoNode:
        # This transformation is just for testing purposes and not correct, see documentation in EuclideanGeoNode.
        _x_shift = 4533770.0
        _y_shift = 5625780.0
        return EuclideanGeoNode(
            self.x - _x_shift, self.y - _y_shift, self.data_source, self.dbref_crs, uuid=self.uuid
        )


class EuclideanGeoNode(GeoNode):
    """
    The Euclidean geo node is a simple geo node based on the simple concept of x and y coordinates and
    the Euclidean distance between two geo nodes. It's mainly for testing purposes and can only be converted to
    DBRef geo nodes, but the conversion is just a simple coordinate shift and with this, probably incorrect.
    """

    def get_distance_to_other_geo_node(self, geo_node_b: EuclideanGeoNode):
        geo_node_b = geo_node_b.to_euclidean()
        return self.__eucldian_distance(geo_node_b)

    def __eucldian_distance(self, geo_node_b: GeoNode):
        min_x = min(self.x, geo_node_b.x)
        min_y = min(self.y, geo_node_b.y)
        max_x = max(self.x, geo_node_b.x)
        max_y = max(self.y, geo_node_b.y)
        return math.sqrt(math.pow(max_x - min_x, 2) + math.pow(max_y - min_y, 2))

    def to_wgs84(self) -> Wgs84GeoNode:
        return self.to_dbref().to_wgs84()

    def to_dbref(self) -> DbrefGeoNode:
        _x_shift = 4533770.0
        _y_shift = 5625780.0
        return DbrefGeoNode(
            self.x + _x_shift, self.y + _y_shift, self.data_source, self.dbref_crs, uuid=self.uuid
        )

    def to_euclidean(self) -> EuclideanGeoNode:
        return self
