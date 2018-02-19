"""
Used for fetching coordinates of a location and computing distance between two locations
Usage: get_distance_in_miles(get_coordinates('Iowa City, IA'), (41.65999984741211,-91.54769897460938))
"""
from geopy.geocoders import Nominatim
from geopy.distance import vincenty


def get_coordinates(location):
    geo_locator = Nominatim()
    geo_location = geo_locator.geocode(location)
    return geo_location.latitude, geo_location.longitude


def get_distance_in_miles(coordinate1, coordinate2):
    return vincenty(coordinate1, coordinate2).miles
