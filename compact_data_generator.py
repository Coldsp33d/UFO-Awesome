import pandas as pd

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


def aggregate_description_by_state(file):
    df = pd.read_csv(file)
    df['state'] = df['state'].mask(df['state'].isin(states) != True)
    data_1 = df.groupby('state').agg({'state': 'count', 'description': ' '.join})
    data_1.to_csv('state_aggr_descr.csv')


aggregate_description_by_state('ufo_awesome_joined.csv')