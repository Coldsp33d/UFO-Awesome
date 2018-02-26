import utils

# load UFO sightings data
df = utils.simple_csv_loader('Data/ufo_awesome_modified.csv', parse_dates=utils.df_date_cols)
# load census data
df_census = utils.simple_csv_loader('Data/census_clean.csv')

#  ---- merge UFO with census data --- # 
df['census_year'] = np.ceil(df.sighted_at.dt.year / 10) * 10  # surrogate column for joining on census year

df = df.merge(
    df_census, on=['municipality', 'state', 'census_year'], how='left'
)

print(df.shape)
print(df.dropna(subset=['municipality', 'state', 'census_year']).shape)


