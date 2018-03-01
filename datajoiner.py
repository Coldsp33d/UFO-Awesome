import pandas as pd
import os

import utils
import datacleaner

#  ---- DATA LOADING ---- #
datasetspec = {
    'UFO'     : (
                    'Data/ufo_awesome_modified.csv', 
                    datacleaner.clean_ufo_data, 
                    {
                        'parse_dates' : utils.df_date_cols, 
                        'compression' : 'gzip'

                }),
    'airport' : ('Data/airport_clean.csv', datacleaner.clean_airport_data, {}),
    'census'  : ('Data/census_clean.csv' , datacleaner.clean_census_data , {}),
    'climate' : ('Data/climate_clean.csv', datacleaner.clean_climate_data, {'parse_dates' : ['date']})
}

dfs = {}
for dataset, (filepath, f, kwargs) in datasetspec.items():
    print('Loading {} data...\t'.format(dataset), end='\r')

    if not os.path.isfile(filepath):
        dfs[dataset] = f(filepath)
    else:
        dfs[dataset] = utils.simple_csv_loader(filepath, **kwargs)

    print('Loading {} data...\tDONE'.format(dataset))


df, df_airport, df_census, df_climate = dfs['UFO'], dfs['airport'], dfs['census'], dfs['climate']

#  ---- DATA JOINING --- 
#
#  ---- merge UFO with airport data --- # 
df = df.merge(df_airport, on=['municipality', 'state'], how='left')

#  ---- merge UFO with census data --- # 
# surrogate column for joining on census year
df['census_year'] = pd.np.ceil(df.sighted_at.fillna(df.reported_at).dt.year / 10) * 10  

df = df.merge(
   df_census, on=['municipality', 'state', 'census_year'], how='left'
)
# --- merge UFO with climate data --- #
df = df.assign(
        temp=df.sighted_at.fillna(df.reported_at) - pd.offsets.MonthBegin(1)  
                                       # floor dataset to the first of each month
     ).merge(
         df_climate, 
         left_on=['temp', 'state'],    # merge on same columns with different labels
         right_on=['date', 'state'],
         how='left'
     ).drop(
         ['temp', 'date'],             # cleanup unnecessary columns
         axis=1
     )

print(df.shape)

utils.simple_csv_saver(df, 'Data/ufo_awesome_joined.csv', compression='gzip')


