import utils
from utils import states, states_rev
import pandas as pd
import glob
import re
import json

from utils import p as column_splitter_pattern


def clean_ufo_data(save : bool=True) -> pd.DataFrame:
    df = utils.load_ufo_data()

    # convert location into municipality and state
    v = utils.split_location_column(df.location)
    v['is_usa'] = ~(v['state'].map(states)).isna()

    df = pd.concat([df, v], axis=1)

    # concatenate elevation and geodata
    df_elev = utils.simple_csv_loader('Data/Input/coordinates_elevation.csv')
    df_elev = pd.concat([
                df_elev.pop('location')\
                       .str.rstrip(', US')\
                       .str.split('\s*,\s*', expand=True)\
                       .iloc[:, :2]\
                       .rename(
                            columns={0 : 'municipality', 1 : 'state'}
                       ), 
                df_elev
        ], axis=1
     )

    # clean up shape column
    df['shape'] = df['shape'].str.strip().mask(df['shape'].eq('unknown'))
    # cleanup state column
    df['state'] = df['state'].mask(~df['state'].isin(states))
    # cleanup description column # TODO - MORE
    df['description'] = df['description']\
                         .str.lower()\
                         .str.replace(r'[^a-z\s&;]', '')\
                         .str.replace('&\S+;', '')\
                         .str.replace('\s+', ' ')
    # add indicator for urban/rural data
    cities = json.load(open('Data/Resources/cities.json'))
    df['is_urban'] = df.municipality.isin(cities)

    df = df.merge(df_elev, on=['municipality', 'state'], how='left')

    if save:
        utils.simple_csv_saver(df, 'Data/ufo_awesome_modified.csv', compression='gzip')

    return df

def clean_census_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original census files from Sayali to be located in the Data/ folder to work.

    Cleans input census files to create and return combined census data
    Data may also be saved to Data/census_clean.csv.

    EXECUTION TIME: 10 seconds (rough estimate)
    '''

    # load geocoded zipcodes from zipcode.json
    zipcodes = pd.io.json.json_normalize(
                list(json.load(open('Data/Resources/zipcodes.json')).values()), 
                record_path=['places'], 
                meta=['post code'], 
                errors='ignore'
    )   
    # cleanup code
    zipcodes = zipcodes.drop(['state', 'latitude', 'longitude'], 1).drop_duplicates(subset=['post code'])
    zipcodes.columns = ['municipality', 'state', 'zipcode']
    zipcodes.municipality = zipcodes.municipality.str.lower()
    zipcodes.zipcode = zipcodes.zipcode.astype(int)
    # load census data with zipcode
    df_census_zip = pd.concat([
                pd.read_csv(
                        f,  usecols=['minimum_age', 'maximum_age', 'gender', 'population', 'zipcode']
                   ).assign(census_year=int(re.search('\d+', f).group())) 
                for f in glob.glob('Data/Input/us-population-by-zip-code/population_by_zip_*.csv')
            ], 
            ignore_index=True
    )
    # remove non-integeral zipcodes
    df_census_zip.zipcode = pd.to_numeric(df_census_zip.zipcode, errors='coerce')
    # drop nulls
    df_census_zip.dropna(inplace=True)
    df_census_zip.zipcode = df_census_zip.zipcode.astype(int)

    # bin data by age into groups 
    v = pd.cut(
            df_census_zip.minimum_age, 
            bins=[0, 18, 65, 100], 
            labels=['children', 'adults', 'senior_citizens'], 
            right=False
    )
    v.name = 'age_group'

    # group and aggregate by census_year, zipcode, age group, and gender
    # unstack on gender
    # merge with geocoded zipcode data
    # merge with other census data for municipality
    df_census_final = df_census_zip.groupby(['census_year', 'zipcode', v.astype(str), 'gender'])\
                                   .population\
                                   .sum()\
                                   .unstack(-2)\
                                   .reset_index()\
                                   .merge(zipcodes, on='zipcode', how='left').groupby(
                                      ['municipality', 'state', 'census_year'], 
                                      as_index=False
                                  ).sum()

    if save:
        utils.simple_csv_saver(df_census_final, 'Data/census_clean.csv')

    return df_census_final

def clean_airport_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original airport codes file airport-codes.json in Data/ to work  

    Cleans airport code file to create and return combined census data
    Data may also be saved to Data/airport_clean.csv.

    '''
    # load nearest airport data
    df_nearest_airport = utils.simple_csv_loader(
                    'Data/Input/nearest_airports.csv', 
                    names=['location', 'ident', 'distance'],
                    header=None,
                    skiprows=1
    )

    df_nearest_airport['location'] = df_nearest_airport.location.str.rstrip(', US')

    p = column_splitter_pattern
    v = df_nearest_airport.pop('location')\
                          .str.rstrip(', US')\
                          .str.split('\s*,\s*', expand=True)\
                          .iloc[:, :2]\
                          .rename(
                             columns={0 : 'municipality', 1 : 'state'}
                         )

    v['municipality'] = v['municipality'].str.lower()
    v['state'] = v['state'].str.upper()

    df_nearest_airport = pd.concat([df_nearest_airport, v], 1)

    # now for the airport
    df_airport = utils.simple_csv_loader(
                        'Data/Input/airport-codes.csv',
                        usecols=['ident', 'name', 'type', 'coordinates', 'type', 'iso_country']
                      )\
                      .query('iso_country == \'US\' and type not in [\'closed\']')\
                      .merge(df_nearest_airport, on='ident')
    # filter on columns
    df_airport = df_airport.loc[:,
        [
        'ident', 
        'name', 
        'municipality',
        'state',
        'coordinates', 
        'type', 
        'distance'
        ]
    ]

    # convert and expand coordinates into separate columns
    df_airport[['lng', 'lat']] = \
            df_airport.pop('coordinates').str.split(',\s*', expand=True).astype(float)
    # remove rows with invalid-coordinates
    df_airport = df_airport.loc[df_airport.lng < -63]
    # lower-case municipality for consistency

    # add column prefix for easy identification
    df_airport.columns = [
            'airport_' +  x if x not in {'municipality', 'state'} else x for x in df_airport.columns 
    ] 

    if save:
        utils.simple_csv_saver(df_airport, 'Data/airport_clean.csv')

    return df_airport

def clean_climate_data(save : bool=True) -> pd.DataFrame:
    df_climate = pd.read_csv(
        'Data/Input/climate_dataset.csv', 
        usecols=['STATE_ABBR', 'YEARMONTH', 'PCP', 'TAVG', 'TMIN', 'TMAX', 'PDSI'],
        dtype={'YEARMONTH' : str}
    ).dropna(
        subset=['PCP', 'TAVG', 'TMIN', 'TMAX', 'PDSI']
    ).reset_index(drop=True)

    df_climate.columns = ['state', 'date', 'precipitation', 'temp_avg', 'temp_min', 'temp_max', 'pdsi']

    c = df_climate.columns.difference(['state', 'date'])
    df_climate[c] = df_climate[c].clip_lower(-99.99).replace(-99.99, pd.np.nan)

    df_climate.date = pd.to_datetime(df_climate.date, format='%Y%m')

    if save:
        utils.simple_csv_saver(df_climate, 'Data/climate_clean.csv')

    return df_climate

if __name__ == '__main__':
    df = clean_census_data(save=True)
    print(df.head(3))
