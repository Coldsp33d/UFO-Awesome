import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('ufo_awesome_joined.csv')

''''
--- Qs.1 Do UFO sightings occur in rural areas?
'''
data = df.groupby('is_urban').agg({'is_usa':'count'})
print(data)
#data.plot.pie(y='is_usa')
data.plot(kind='pie', y = 'is_usa', autopct='%1.1f%%',
 startangle=90, shadow=False, legend = True, fontsize=12)
plt.xlabel("Seen in Urban Area?")
plt.ylabel("Based on sightings in USA")
plt.show()


''''
--- Qs.2 Do UFO sightings occur in areas within 25 miles of the aiport
'''
cols = 'airport_distance'
x5 = df.loc[df[cols]<=5, cols]
x10 = df.loc[(df[cols]> 5) & (df[cols] <= 10), cols]
x15 = df.loc[(df[cols]> 10) & (df[cols] <= 15), cols]
x20 = x = df.loc[(df[cols]> 15) & (df[cols] <= 20), cols]
x25 = x = df.loc[(df[cols]> 20) & (df[cols] <= 25), cols]
x25_ = df.loc[df[cols]>25, cols]
print(x5.shape)
print(x10.shape)
print(x15.shape)
print(x20.shape)
print(x25.shape)
print(x25_.shape)


'''
----  No of sightings and duration of observation
'''
cols ='duration'
x30 = df.loc[df[cols]<=30, cols]
x60 = df.loc[(df[cols]> 30) & (df[cols] <= 60), cols]
x300 = df.loc[(df[cols]> 60) & (df[cols] <= 300), cols]
x1800  = df.loc[(df[cols]> 300) & (df[cols] <= 1800), cols]
x3600 = df.loc[(df[cols]> 1800) & (df[cols] <= 3600), cols]
x3600_ = df.loc[(df[cols]> 3600),cols]
print(x30.shape)
print(x60.shape)
print(x300.shape)
print(x1800.shape)
print(x3600.shape)
print(x3600_.shape)