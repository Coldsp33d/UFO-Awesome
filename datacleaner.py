import utils
from utils import states
import pandas as pd
import glob
import re
import json

states_rev = {v : k for k, v in states.items()}

def clean_census_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original census files from Sayali to be located in the Data/ folder to work.

    Cleans input census files to create and return combined census data
    Data may also be saved to Data/census_clean.csv.

    EXECUTION TIME: 10-15 seconds (rough estimate)
    '''

    # load census data for 1991-2000 
    i = pd.read_csv(
            'Data/census2000.csv', usecols=['NAME','STNAME','ESTIMATESBASE2000'], encoding='latin-1'
    )
    i.columns = ['municipality', 'state', 'census']  # rename columns
    i['census_year'] = 2000     # set the year

    i.state = i.state.str.strip().map(states_rev)    # map state name to state code 
    i = i[  ~i.municipality.isin(states.values()) 
          & ~i.municipality.str.contains('Balance')] # the column needs some cleaning

    # load census data for 2001-2010    
    j = pd.read_csv(
            'Data/census2010/PEP_2016_PEPANNRES_with_ann.csv', 
            usecols=['GEO.display-label','rescen42010'], 
            encoding='latin-1', 
            header=0, 
            skiprows=[1]    # skip the first row as it isn't needed
    )
    j.columns = ['location', 'census']
    j['census_year'] = 2010
    # split location into two columns - municipality + state
    j[['municipality', 'state']] = j.pop('location').str.rsplit(',', 1, expand=True) 
    # reorder columns 
    j = j.reindex(columns=['municipality', 'state','census', 'census_year'])
    # clean and fix state for consistency
    j.state = j['state'].str.strip().map(states_rev)

    # join 2000 and 2010 census dataframes vertically
    df_census = pd.concat([i, j], ignore_index=True)
    # clean municipality column - remove spaces and descriptive terms
    df_census.municipality = df_census.municipality\
                          .str.lower()\
                          .str.replace(r'\s*\(.*?\)\s*', '')\
                          .str.replace(
                            'city|town|village|county|borough|municipality', ''
                         ).str.strip()

    # convert census column to integer. Only consider the uppermost level of population for simplicity
    # and resolve census across various geographic granularities
    df_census['census'] = pd.to_numeric(df_census.census, errors='coerce')\
                            .groupby(
                                [df_census.municipality, df_census.census_year]
                           ).transform('max')
    # remove duplicates and rows with NaNs
    df_census = df_census.drop_duplicates(
                                subset=['municipality', 'census_year']
                        ).dropna()
    df_census.census = df_census.census.astype(int)

    # load geocoded zipcodes from zipcode.json
    zipcodes = pd.io.json.json_normalize(
                list(json.load(open('Data/zipcodes.json')).values()), 
                record_path=['places'], 
                meta=['post code'], 
                errors='ignore'
    )   
    # cleanup code
    zipcodes = zipcodes.drop('state', 1).drop_duplicates(subset=['post code'])
    zipcodes.columns = ['lat', 'lng', 'municipality', 'state', 'zipcode']
    zipcodes.municipality = zipcodes.municipality.str.lower()

    # load census data with zipcode
    df_census_zip = pd.concat([
                pd.read_csv(
                        f,  usecols=['minimum_age', 'maximum_age', 'gender', 'population', 'zipcode']
                   ).assign(census_year=int(re.search('\d+', f).group())) 
                for f in glob.glob('Data/us-population-by-zip-code/population_by_zip_*.csv')
            ], 
            ignore_index=True
    )
    # remove non-integeral zipcodes
    df_census_zip.zipcode = df_census_zip.zipcode.mask(~df_census_zip.zipcode.astype(str).str.isdigit())
    # drop nulls
    df_census_zip.dropna(inplace=True)

    # bin data by age into groups 
    v = pd.cut(
            df_census_zip.minimum_age, 
            bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90], 
            labels=['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89'], 
            right=False
    )
    v.name = 'age_group'

    # group and aggregate by census_year, zipcode, age group, and gender
    # unstack on gender
    # merge with geocoded zipcode data
    # merge with other census data for municipality
    df_census_final = df_census_zip.groupby(['census_year', 'zipcode', v, 'gender'])\
                                   .population\
                                   .sum()\
                                   .unstack()\
                                   .reset_index()\
                                   .merge(zipcodes, on='zipcode')\
                                   .merge(
                                      df_census.drop('census', 1), 
                                      on=['municipality', 'state', 'census_year']
                                  )

    if save:
        utils.simple_csv_saver(df_census_final, 'Data/census_clean.csv')

    return df_final


def clean_airport_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original airport codes file airport-codes.json in Data/ to work  

    Cleans airport code file to create and return combined census data
    Data may also be saved to Data/airport_codes_clean.csv.

    '''
    # load nearest airport data
    df_nearest_airport = utils.simple_csv_loader(
                    'Data/nearest_airports.csv', 
                    names=['location', 'ident', 'distance'],
                    header=None,
                    skiprows=1
    )
    df_nearest_airport['location'] = df_nearest_airport.location.str.rstrip(', US')

    p = r'''
    (?P<municipality>           # first capture group - capture municipality
        [^\(]+                  # anything that is not a parenthesis 
    )
    .*                          # greedy match
    ,                           # match the last comma in the string
    \s*                         # strip spaces
    (?P<state>                  # second capture group - capture state
        .*                      # greedy match (state)    
    )'''
    v = df_nearest_airport.pop('location')\
                          .str.extract(
                                p, expand=True, flags=re.VERBOSE
                         ).dropna()\
                          .applymap(str.strip)

    v['municipality'] = v['municipality'].str.lower()
    v['state'] = v['state'].str.upper()

    df_nearest_airport = pd.concat([df_nearest_airport, v], 1)

    # now for the airport
    df_airport = utils.simple_csv_loader(
                        'Data/airport-codes.csv',
                        usecols=['ident', 'name', 'type', 'coordinates', 'type', 'iso_country']
                      )\
                      .query('iso_country == \'US\' and type != \'closed\'')\
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
        'Data/climate_dataset.csv', 
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
