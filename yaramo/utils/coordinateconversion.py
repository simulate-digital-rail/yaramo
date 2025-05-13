"""
Copyright (c) 2021 DB Netz AG and others.

All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v2.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v20.html


-------------

The DBRef and WGS84 conversions are taken from the Eclipse Signalling Engineering Toolbox (https://github.com/eclipse-set/set/tree/main)

See
https://github.com/eclipse-set/set/blob/main/java/bundles/org.eclipse.set.feature.siteplan/src/org/eclipse/set/feature/siteplan/positionservice/PositionServiceImpl.java
and
https://github.com/eclipse-set/set/blob/main/java/bundles/org.eclipse.set.ppmodel.extensions/src/org/eclipse/set/ppmodel/extensions/geometry/CoordinateExtensions.xtend
for the original sources.
"""
import pyproj

EPSG_3857_STRING = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"


def transform_dbref_to_wgs84(x: float, y: float, coordinate_str: str):
    proj_dbref_str = __get_proj_dbref_str(coordinate_str)

    # Step 1 DBRef to Pseudo-Mercator:
    transformer = pyproj.Transformer.from_crs(crs_from=proj_dbref_str, crs_to=EPSG_3857_STRING)
    x, y = transformer.transform(x, y)

    # Step 2 Pseudo-Mercator to WGS84:
    transformer_2 = pyproj.Transformer.from_crs(crs_from=3857, crs_to=4326)
    return transformer_2.transform(x, y)


def transform_wgs84_to_dbref(x: float, y: float, coordinate_str: str):
    proj_dbref_str = __get_proj_dbref_str(coordinate_str)

    # Step 2 WGS84 to Pseudo-Mercator:
    transformer_2 = pyproj.Transformer.from_crs(crs_from=4326, crs_to=3857)
    x, y = transformer_2.transform(x, y)

    # Step 1 Pseudo-Mercator to DBRef:
    transformer = pyproj.Transformer.from_crs(crs_from=EPSG_3857_STRING, crs_to=proj_dbref_str)
    return transformer.transform(x, y)


def __get_proj_dbref_str(coordinate_str: str):
    CRS_CR0_STRING = "+proj=tmerc +lat_0=0 +lon_0=6  +k=1 +x_0=2500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7 +units=m +no_defs"
    CRS_DR0_STRING = "+proj=tmerc +lat_0=0 +lon_0=9  +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7 +units=m +no_defs"
    CRS_ERO_STRING = "+proj=tmerc +lat_0=0 +lon_0=12 +k=1 +x_0=4500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7 +units=m +no_defs"
    CRS_FRO_STRING = "+proj=tmerc +lat_0=0 +lon_0=15 +k=1 +x_0=5500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7 +units=m +no_defs"

    match coordinate_str:
        case "CR0":
            return CRS_CR0_STRING
        case "DR0":
            return CRS_DR0_STRING
        case "ER0":
            return CRS_ERO_STRING
        case "FR0":
            return CRS_FRO_STRING
        case _:
            raise ValueError("No valid coordinate_str given. Supported are: CR0, DR0, ER0 and FR0.")
