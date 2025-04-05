from shapely.geometry import (
    shape,
    Point,
    LineString,
    Polygon,
    MultiPolygon,
    MultiLineString,
    MultiPoint,
)
from shapely.geometry.base import BaseGeometry
from geoalchemy2.shape import from_shape
from shapely.geometry import mapping, shape

def force_coords_3d(coords):
    """Converte uma lista de coordenadas 2D para 3D"""
    return [
        (x, y, z if len(coord) == 3 else 0.0)
        for coord in coords
        for x, y, *rest in [coord]
        for z in [rest[0] if rest else 0.0]
    ]


def force_ring_3d(ring):
    """Converte um anel (lista de coordenadas) para 3D"""
    return force_coords_3d(ring)


def force_geom_3d(geom: BaseGeometry) -> BaseGeometry:
    """Converte qualquer geometria Shapely para 3D"""
    if geom.is_empty:
        return geom

    if geom.geom_type == "Point":
        x, y = geom.coords[0][:2]
        z = geom.coords[0][2] if geom.has_z else 0.0
        return Point(x, y, z)

    elif geom.geom_type == "LineString":
        return LineString(force_coords_3d(geom.coords))

    elif geom.geom_type == "Polygon":
        exterior = force_ring_3d(geom.exterior.coords)
        interiors = [force_ring_3d(ring.coords) for ring in geom.interiors]
        return Polygon(exterior, interiors)

    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([force_geom_3d(poly) for poly in geom.geoms])

    elif geom.geom_type == "MultiLineString":
        return MultiLineString([force_geom_3d(line) for line in geom.geoms])

    elif geom.geom_type == "MultiPoint":
        return MultiPoint([force_geom_3d(point) for point in geom.geoms])

    else:
        raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def geojson_to_postgis_geom3d(geojson_geom: dict, srid=4326):
    """Converte um GeoJSON geometry em uma geometria GeoAlchemy2 3D"""
    shapely_geom = shape(geojson_geom)
    geom_3d = force_geom_3d(shapely_geom)
    return from_shape(geom_3d, srid=srid)


def force_geom_2d(geom):
    """Remove coordenadas Z de qualquer geometria shapely"""
    if geom.is_empty:
        return geom

    if geom.geom_type == "Point":
        x, y = geom.xy[0][0], geom.xy[1][0]
        return Point(x, y)

    elif geom.geom_type == "LineString":
        return LineString([(x, y) for x, y, *_ in geom.coords])

    elif geom.geom_type == "Polygon":
        exterior = [(x, y) for x, y, *_ in geom.exterior.coords]
        interiors = [[(x, y) for x, y, *_ in ring.coords] for ring in geom.interiors]
        return Polygon(exterior, interiors)

    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([force_geom_2d(g) for g in geom.geoms])

    elif geom.geom_type == "MultiLineString":
        return MultiLineString([force_geom_2d(g) for g in geom.geoms])

    elif geom.geom_type == "MultiPoint":
        return MultiPoint([force_geom_2d(g) for g in geom.geoms])

    else:
        raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def force_2d(geom):
    """Remove o eixo Z de qualquer geometria."""
    geojson_geom = mapping(geom)

    def drop_z(coords):
        return [(x, y) for x, y, *_ in coords]

    if geojson_geom["type"] == "Polygon":
        new_coords = [drop_z(ring) for ring in geojson_geom["coordinates"]]
        return shape({"type": "Polygon", "coordinates": new_coords})

    elif geojson_geom["type"] == "MultiPolygon":
        new_coords = [
            [drop_z(ring) for ring in polygon]
            for polygon in geojson_geom["coordinates"]
        ]
        return shape({"type": "MultiPolygon", "coordinates": new_coords})

    else:
        raise ValueError(f"Unsupported geometry type: {geojson_geom['type']}")
