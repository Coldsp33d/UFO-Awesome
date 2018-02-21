"""
Used for fetching coordinates of a location and computing distance between two locations
Usage: get_distance_in_miles(get_coordinates('Iowa City, IA'), (41.65999984741211,-91.54769897460938))
"""
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import json

coordinates_map = {}
with open('data/coordinates.json', 'r') as fp:
    coordinates_map = json.load(fp)

geo_locator = Nominatim(timeout=None)


def get_coordinates(location):
    if location in coordinates_map:
        return coordinates_map[location]
    print(location)
    geo_location = geo_locator.geocode(location, timeout=None)
    if not geo_location:
        coordinates_map[location] = ''
        save_coordinates(coordinates_map)
        return coordinates_map[location]
    coordinates_map[location] = geo_location.latitude, geo_location.longitude
    save_coordinates(coordinates_map)
    return coordinates_map[location]


def save_coordinates(coordinates_map):
    with open('data/coordinates.json', 'w') as fp:
        json.dump(coordinates_map, fp)


def get_coordinates_list(locations):
    coordinate_list = []
    for location in locations:
        coordinate_list.append(get_coordinates(location))
    return coordinate_list


def get_distance_in_miles(coordinate1, coordinate2):
    return vincenty(coordinate1, coordinate2).miles