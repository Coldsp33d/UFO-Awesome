import utils
import pandas as pd

# load data
df = utils.simple_csv_loader(
            'Data/ufo_awesome_modified.csv', 
            parse_dates=utils.df_date_cols,
            compression='gzip'
)
df_airport = utils.simple_csv_loader('Data/airport_codes_clean.csv')

df_census = utils.simple_csv_loader('Data/census_clean.csv')

#  ---- merge UFO with census data --- # 
# surrogate column for joining on census year
df['census_year'] = pd.np.ceil(df.sighted_at.fillna(df.reported_at).dt.year / 10) * 10  

df = df.merge(
    df_census, on=['municipality', 'state', 'census_year'], how='left'
)

#  ---- merge UFO with airport data --- # 
#df = df.merge(df_airport, on='municipality', how='left')

utils.simple_csv_saver(df, 'Data/ufo_awesome_joined.csv', compression='gzip')
