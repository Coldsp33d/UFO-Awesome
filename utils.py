import json
import pandas as pd
import re

# global constant
df_date_cols = ['sighted_at', 'reported_at']

# General dataloader functions
def simple_json_loader(filepath : str, lines : bool=True) -> pd.DataFrame:
    ''' Reads a .json file using pd.read_json '''
    return pd.read_json(filepath, lines=lines)


def simple_csv_loader(filepath : str, **kwargs : dict) -> pd.DataFrame:
    encoding = kwargs.get('encoding', 'latin-1') # default encoding
    return pd.read_csv(filepath, encoding=encoding, **kwargs)


def default_json_loader(filepath : str) -> pd.DataFrame:
    ''' Reads and loads data line-wise, use when pd.read_json cannot be used ''' 
    data = []
    with open(filepath) as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except ValueError:
                pass        # TODO fix buggy data

    return pd.DataFrame.from_records(data)


def simple_csv_saver(df : pd.DataFrame, filepath : str):
    df.to_csv(filepath)


def load_ufo_data() -> pd.DataFrame:
    ''' Data loader code for the ufo_awesome dataset (currently supports only JSON) '''

    # constants
    df_cols = [
              'sighted_at', 
              'reported_at', 
              'location', 
              'duration', 
              'shape', 
              'description',
          ]

    try:  # attempt load with pd.read_json
        '''
        Can be used once ufo_awesome.json has been corrected. 
        To fix the data, run `python3.6 fix_json_data.py`

        ''' 
        df = simple_json_loader('Data/ufo_awesome.json', lines=True)
    except ValueError:
          # fallback to loopy implementation reader (filters out corrupt data)
        df = default_json_loader('Data/ufo_awesome.json')

    df[df_date_cols] = df[df_date_cols]\
                       .astype(str)\
                       .apply(
                            pd.to_datetime, errors='coerce', format='%Y%m%d'
                       )

    return df.reindex(columns=df_cols).replace('', pd.np.nan)


def split_location(df : pd.DataFrame) -> pd.DataFrame:
    states = json.load(open('Data/states.json'))
    p = r'''
    (?P<municipality>           # first capture group - capture municipality
        [^\(]+                  # anything that is not a parenthesis 
    )
    .*                          # greedy match
    ,                           # match the last comma in the string
    \s*                         # strip spaces
    (?P<state>                  # second capture group - capture state
        .*                      # greedy match (state)    
    )'''

    v = df.location.str.extract(
                p, expand=True, flags=re.VERBOSE)\
          .applymap(str.strip)

    v['municipality'] = v['municipality'].str.lower()
    v['state'] = v['state'].str.upper()
    v['is_usa'] = ~(v['state'].map(states)).isna()

    return pd.concat([df, v], axis=1)


if __name__ == '__main__':
    df = load_data()
    print(df.head(3))
