"""
Used for fetching coordinates of a location and computing distance between two locations
Usage: get_distance_in_miles(get_coordinates('Iowa City, IA'), (41.65999984741211,-91.54769897460938))
"""

from typing import Union

from utils import simple_csv_loader

import json
import os
import requests
import geocoder

import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

# initialise geocoder 
geo_locator = Nominatim(timeout=None)

# load coordinates into memory
coordinates = {}
if os.path.isfile('Data/coordinates.json'):
    coordinates = json.load(open('Data/coordinates.json'))

# load zipcodes into memory
zipcodes = {}
if os.path.isfile('Data/zipcodes.json'):
    zipcodes = json.load(open('Data/zipcodes.json'))


def addr2geo(address : str) -> dict:
    ''' RESTfully geocodes human readable address '''
    if address in coordinates:
        return coordinates[address]
    
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': address}
    r = requests.get(url, params=params, timeout=5)
    
    return r.json()['results'][0]['geometry']['location']
    

def addr2geo2(address : str) -> dict:
    ''' uses `geocoder` API to geocode human readable addresses '''
    if address in coordinates:
        return coordinates[address]
    
    return dict(zip(['lat', 'long'], geocoder.google(address).latlng))


def addr2geo3(address : str) -> Union[dict, None]:
    ''' uses the `geopy` API to geocode human readable addresses ''' 
    if address in coordinates:
        return coordinates[address]

    try:
        geo = geo_locator.geocode(address + ', United States of America', timeout=None)
        return {'lat' : geo.latitude, 'lng' : geo.longitude}
    except (AttributeError, geopy.exc.GeocoderTimedOut, geopy.exc.GeocoderServiceError):
        pass


def zip2geo(code : str) -> dict:
    ''' geocode location by zipcode '''  
    if code in zipcodes:
        return zipcodes[code]

    return requests.get("http://api.zippopotam.us/us/{}".format(code), timeout=None).json()

if __name__ == '__main__':
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
        
        print('{} - {} - {:2f}/100'.format(i, len(unique_mun), i / len(unique_mun) * 100))
        if i % 50 == 0:
            coordinates.update(json.load(open('Data/coordinates.json')))
            json.dump(coordinates, open('Data/coordinates.json', 'w'))
