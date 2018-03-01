import json
import numpy as np
import pandas as pd
import re

import geopy
from geopy.distance import vincenty

# global variables
df_date_cols = ['sighted_at', 'reported_at']

states = json.load(open('Data/states.json'))
states_rev = {v : k for k, v in states.items()}
state_codes, state_names = zip(*states.items())

p =  r'''
    (?P<municipality>           # first capture group - capture municipality
        [^\(]+                  # anything that is not a parenthesis 
    )
    .*                          # greedy match
    ,                           # match the last comma in the string
    \s*                         # strip spaces
    (?P<state>                  # second capture group - capture state
        .*                      # greedy match (state)    
    )'''

# Ned Batchelder's `chunkify` function
def chunkify(l, n): 
    for i in range(0, len(l), n):
        yield l[i:i + n]

# General dataloader functions
def simple_json_loader(filepath : str, lines : bool=True) -> pd.DataFrame:
    ''' Reads a .json file using pd.read_json '''
    return pd.read_json(filepath, lines=lines)

def simple_csv_loader(filepath : str, **kwargs : dict) -> pd.DataFrame:
    encoding = kwargs.get('encoding', 'latin-1') # default encoding
    return pd.read_csv(filepath, encoding=encoding, **kwargs)

def default_json_loader(filepath : str) -> pd.DataFrame:
    ''' Reads and loads data line-wise, use when pd.read_json cannot be used ''' 
    data = []
    with open(filepath) as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except ValueError:
                pass        # TODO fix buggy data

    return pd.DataFrame.from_records(data)

def simple_csv_saver(df : pd.DataFrame, filepath : str, **kwargs : dict):
    df.to_csv(filepath, index=False, **kwargs)

def load_ufo_data() -> pd.DataFrame:
    ''' Data loader code for the ufo_awesome dataset (currently supports only JSON) '''

    # constants
    df_cols = [
              'sighted_at', 
              'reported_at', 
              'location', 
              'duration', 
              'shape', 
              'description',
          ]

    try:  # attempt load with pd.read_json
        '''
        Can be used once ufo_awesome.json has been corrected. 
        To fix the data, run `python3.6 fix_json_data.py`

        ''' 
        df = simple_json_loader('Data/ufo_awesome.json', lines=True)
    except ValueError:
          # fallback to loopy implementation reader (filters out corrupt data)
        df = default_json_loader('Data/ufo_awesome.json')

    df[df_date_cols] = df[df_date_cols]\
                       .astype(str)\
                       .apply(
                            pd.to_datetime, errors='coerce', format='%Y%m%d'
                       )

    return df.reindex(columns=df_cols).replace('', pd.np.nan)

def split_location_column(ser : pd.Series) -> pd.DataFrame:
    '''
    Split `location` Series into a dataframe of municipality and state
    
    This is a separate function since it is needed in many places 
    '''

    v = ser.str.extract(
                p, expand=True, flags=re.VERBOSE)\
          .applymap(str.strip)

    v['municipality'] = v['municipality'].str.lower()
    v['state'] = v['state'].str.upper()

    return v

def get_distance_in_miles(coordinate1, coordinate2):
    return vincenty(coordinate1, coordinate2).miles

# courtesy https://stackoverflow.com/a/29546836/4909087
def fast_haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    '''
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

if __name__ == '__main__':
    df = load_data()
    print(df.head(3))
