from shapely.geometry import mapping

def polygon_to_geojson(polygon):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(polygon),
                "properties": {}
            }
        ]
    }