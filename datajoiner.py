import utils

import pandas as pd

# ---- data loading --- #
# load ufo data
df = utils.simple_csv_loader(
            'Data/ufo_awesome_modified.csv', 
            parse_dates=utils.df_date_cols,
            compression='gzip'
)
# load aiport data
df_airport = utils.simple_csv_loader('Data/airport_codes_clean.csv')
# load combined census and geodata
df_census = utils.simple_csv_loader('Data/census_clean.csv')
# separate geodata from census data for easier management
df_geodata = df_census[['municipality', 'state', 'zipcode', 'lat', 'lng']].drop_duplicates()
df_census = df_census.drop(['zipcode', 'lat', 'lng'], 1)

#  ---- merge UFO with airport data --- # 
# df = df.merge(df_geodata, on=['municipality', 'state'], how='left')\
#        .merge(df_airport, on=['municipality', 'state'], how='left')


# df['dist_from_airport'] = utils.fast_haversine(df.lng, df.lat, df.airport_lng, df.airport_lat)

# cols = df.columns.difference(['municipality', 'state'])
# f = dict.fromkeys(cols, 'first'); f['dist_from_airport'] = 'min'

# df.groupby(['municipality', 'state'], as_index=False).agg(f)


#  ---- merge UFO with census data --- # 
# surrogate column for joining on census year
df['census_year'] = pd.np.ceil(df.sighted_at.fillna(df.reported_at).dt.year / 10) * 10  

df = df.merge(
    df_census, on=['municipality', 'state', 'census_year'], how='left'
)


utils.simple_csv_saver(df, 'Data/ufo_awesome_joined.csv', compression='gzip')


# --- merge UFO with climate data --- #
# floor date to beginning of month for easy merge later
df = df.assign(
         temp=df.sighted_at.fillna(df.reported_at) - pd.offsets.MonthBegin(1)
     ).merge(
         df_climate, 
         left_on=['temp', 'state'],    # merge on same columns with different labels
         right_on=['date', 'state']
     ).drop(
         ['temp', 'date'],             # cleanup unnecessary columns
         axis=1
     )



