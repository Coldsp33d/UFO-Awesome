import utils
import pandas as pd

# ----- census saver (normalized and non-normalized - total 4 CSVs) ---- #
df = utils.simple_csv_loader(                                                          
        'Data/ufo_awesome_joined.csv',              
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

z_2010 = z_2010.apply(
                    pd.qcut, 
                    q=5, 
                    axis=0, 
                    duplicates='drop'
               ).apply(
                    lambda x: x.cat.codes
               ).iloc[:top_n]

z_2000 = z_2000.apply(
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

# ---- elevation saver ----- #
v = pd.cut(df.elevation, [-500, 0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500])
result = df.groupby(v)\
           .agg({
                  'elevation' : 'size', 
                  'precipitation' : 'mean', 
                  'pdsi' : 'mean',
                  'temp_avg' : 'mean'
            })\
            .rename(columns={'elevation' : 'num_sightings'})\
            .reset_index()

utils.simple_csv_saver(result,' Data/Viz/elev.csv')           

df  = pd.read_csv('Data/Viz/elev.csv', index_col=[0])
df2 = (df - df.mean()) / (df.max() - df.min())
df2.to_csv('Data/Viz/elev_norm.csv')   


# ---- distance v/s duration query ---- #                           

i = pd.cut(
        df.duration, 
        bins=[0, 60, 300, 3600, pd.np.inf], 
        labels=['<1min', '1-5 min', '1hr', '>1hr'])
j = pd.cut(
        df.airport_distance, 
        bins=[0, 5, 10, 15, 20, 25, pd.np.inf], 
        labels=['<5mi', '5-10mi', '10-15mi', '15-20mi', '20-25mi', '>25mi']
)

print(i.groupby(j).value_counts().unstack(-1, fill_value=0))
