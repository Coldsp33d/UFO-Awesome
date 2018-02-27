"""
Used for fetching coordinates of a location and computing distance between two locations
Usage: get_distance_in_miles(get_coordinates('Iowa City, IA'), (41.65999984741211,-91.54769897460938))
"""

from utils import simple_csv_loader

import json
import os
import requests
import geocoder

from geopy.geocoders import Nominatim
from geopy.distance import vincenty

geo_locator = Nominatim(timeout=None)

coordinates = {}
if os.path.isfile('Data/coordinates.json'):
    coordinates = json.load(open('Data/coordinates.json', 'r'))

def addr2geo(address):
    # uses 
    if address in coordinates:
        return {'address' : coordinates[address]}
    
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': address}
    r = requests.get(url, params=params, timeout=5)
    
    return r.json()['results'][0]['geometry']['location']
    

def addr2geo2(address):
    if address in coordinates:
        return {'address' : coordinates[address]}
    
    return geocoder.google(address).latlng

def addr2geo3(address):
    if address in coordinates:
        return {'address' : coordinates[address]}

    geo = geo_locator.geocode(address + ', United States of America', timeout=None)

    try:
        return {'lat' : geo.latitude, 'lng' : geo.longitude}
    except AttributeError:
        return {'lat' : None, 'lng' : None}


def zip2geo(code):
    return requests.get("http://api.zippopotam.us/us/{}".format(code), timeout=5).json()

if __name__ == '__main__':
    coordinates = {}
    df = simple_csv_loader(
            'Data/ufo_awesome_modified.csv', 
            usecols=['municipality', 'state', 'is_usa'],
            compression='gzip'
    )

    unique_mun = df.loc[
                      df.is_usa, ['municipality', 'state']
                ].dropna()\
                 .apply(', '.join, axis=1)\
                 .unique()\
                 .tolist()



    
    geo_f = addr2geo
    for i, line in enumerate(unique_mun):
        try:
            coordinates[line] = geo_f(line)
        except (IndexError, requests.ConnectionError, requests.exceptions.ReadTimeout):
            print('           Error on {}           '.format(line))
            continue
        
        print('{} - {} - {:2f}/100'.format(i, len(unique_mun), i / len(unique_mun) * 100), end='\r')
        if i % 50 == 0:
            json.dump(coordinates, open('Data/coordinates.json', 'w'))
