import utils

df = utils.simple_csv_loader(                                                          
        'Data/ufo_awesome_joined.csv',             
        #usecols=['description', 'state'],           
        compression='gzip',                         
)

g = df.groupby(['shape', 'census_year'])
x = g['children','adults','senior_citizens'].first()
y = df.groupby(['shape', 'census_year']).adults.count()
y.name = 'total_sightings'

z = pd.concat([x, y], 1).dropna().reset_index(level=1)

z_2000 = z[z.census_year == 2000].drop('census_year', 1)
z_2010 = z[z.census_year == 2010].drop('census_year', 1)

top_n = 10

z_2010.apply(
	pd.qcut, 
	q=5, 
	axis=0, 
	duplicates='drop'
).apply(
	lambda x: x.cat.codes
).iloc[:top_n]

z_2000.apply(
	pd.qcut, 
	q=5, 
	axis=0, 
	duplicates='drop'
).apply(
	lambda x: x.cat.codes
).iloc[:top_n]

z_2010_norm = (z_2010 - z_2010.mean()) / (z_2010.max() - z_2010.min())
z_2000_norm = (z_2000 - z_2000.mean()) / (z_2000.max() - z_2000.min())

z_2000.to_csv('Data/Viz/census_2000.csv')
z_2010.to_csv('Data/Viz/census_2010.csv')
z_2000_norm.to_csv('Data/Viz/census_2000_norm.csv')
z_2010_norm.to_csv('Data/Viz/census_2010_norm.csv')

