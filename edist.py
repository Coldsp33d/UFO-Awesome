import utils 
from utils import states
from keyword_extraction import preprocess

import pandas as pd
import json

keywords = json.load(open('Data/Resources/keywords.json', 'r')) 

df = utils.simple_csv_loader(
            'Data/ufo_awesome_joined.csv', 
            usecols=['description', 'state'], 
            compression='gzip', 
    )

v = df.assign(
        description=df.description.apply(preprocess), 
        state=df.state.mask(~df.state.isin(states.keys()))
     ).groupby('state', squeeze=True)\
      .description.apply(' '.join)\
      .apply(
          lambda x: set(x.split()).intersection(keywords[:64])
     ).apply(' '.join, 1)\
      .str.split(expand=True)\
      .fillna('')\
      .apply(' '.join, 1)\
      .str.replace('\s+', ' ')\
      .str.get_dummies(sep=' ')\
      .astype(str)\
      .loc[df.state.value_counts().index]\
      .agg(
           lambda x: int(''.join(x), 2), axis=1
     ).values

edit_distances = pd.DataFrame(v ^ v[:, None]).applymap(lambda x: sum(map(int, bin(x)[2:])))

v = edit_distances.melt() 
v.insert(1, 1, v.groupby('variable').cumcount())
v.columns = ['x', 'y', 'edit_distance']



print(edit_distances)