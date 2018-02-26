import utils
from utils import states
import pandas as pd

states_rev = {v : k for k, v in states.items()}

def clean_census_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original census files from Sayali to be located in the Data/ folder to work.

    Cleans input census files to create and return combined census data
    Data may also be saved to Data/census_clean.csv.

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

    if save:
        utils.simple_csv_saver(df_census, 'Data/census_clean.csv')

    return df_census

def clean_airport_data(save : bool=True) -> pd.DataFrame:
    ''' 
    Requires original airport codes file airport-codes.json in Data/ to work  

    Cleans airport code file to create and return combined census data
    Data may also be saved to Data/airport_codes_clean.csv.

    '''
    df_airport = utils.simple_json_loader('Data/airport-codes.json')\
                      .query('iso_country == \'US\' and type != \'closed\'')
    # filter on columns
    df_airport = df_airport.loc[:, ['coordinates', 'elevation_ft', 'municipality', 'name', 'type']]
    # convert and expand coordinates into separate columns
    df_airport[['airport_lon', 'airport_lat']] = df_airport.pop('coordinates').str.split(',\s*', expand=True).astype(float)
    # remove rows with invalid-coordinates
    df_airport = df_airport[df_airport.airport_lon < -63]
    # lower-case municipality for consistency
    df_airport.municipality = df_airport.municipality.str.lower()

    if save:
        utils.simple_csv_saver(df_airport, 'Data/airport_codes_clean.csv')

    return df_airport


if __name__ == '__main__':
    df = clean_census_data(save=True)
    print(df.head(3))
