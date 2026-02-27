# backend/schemas/routing.py

def latlon_to_grid(lat, lon):
    x = int((lat - 23.0) * 100)
    y = int((lon - 90.0) * 100)
    return (x, y)