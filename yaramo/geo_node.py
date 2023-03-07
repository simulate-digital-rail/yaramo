from abc import ABC, abstractmethod

from yaramo.base_element import BaseElement
from yaramo.geo_point import DbrefGeoPoint, GeoPoint, Wgs84GeoPoint


class GeoNode(ABC, BaseElement):
    """This is the baseclass of specific GeoNodes that use different coordinate systems.
    
    A GeoNode refers to a GeoPoint as a means of location.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geo_point: GeoPoint = None

    @abstractmethod
    def get_distance_to_other_geo_node(self, geo_node_b: "GeoNode"):
        """Returns to distance to the given other GeoNode."""

        pass

    @abstractmethod
    def to_wgs84(self) -> "Wgs84GeoNode":
        pass

    @abstractmethod
    def to_dbref(self) -> "DbrefGeoNode":
        pass

    def to_serializable(self):
        """Creates two serializable dictionaries out of the GeoNode object.

        This creates a dictionary with immediately serializable attributes and
        references (uuids) to attributes that are objects.
        This creates a second dictionary where said objects are serialized (by deligation).

        See the description in the BaseElement class.

        Returns:
            A serializable dictionary and a dictionary with serialized objects (GeoPoints).
        """
        attributes = self.__dict__
        references = {
            "geo_point": self.geo_point.uuid,
        }
        point_object, point_serialized = self.geo_point.to_serializable()
        return {**attributes, **references}, {self.geo_point.uuid: point_object, **point_serialized}


class Wgs84GeoNode(GeoNode):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = Wgs84GeoPoint(x, y)

    def get_distance_to_other_geo_node(self, geo_node_b: "Wgs84GeoNode"):
        return self.geo_point.get_distance_to_other_geo_point(geo_node_b.geo_point)

    def to_wgs84(self) -> "Wgs84GeoNode":
        return self

    def to_dbref(self) -> "DbrefGeoNode":
        geopoint = self.geo_point.to_dbref()
        return DbrefGeoNode(geopoint.x, geopoint.y)


class DbrefGeoNode(GeoNode):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.geo_point = DbrefGeoPoint(x, y)

    def get_distance_to_other_geo_node(self, geo_node_b: "DbrefGeoNode"):
        return self.geo_point.get_distance_to_other_geo_point(geo_node_b.geo_point)

    def to_wgs84(self) -> "Wgs84GeoNode":
        raise NotImplementedError

    def to_dbref(self) -> "DbrefGeoNode":
        return self
