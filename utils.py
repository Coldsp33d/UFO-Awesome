import json
import pandas as pd

# constants
df_cols = [
          'sighted_at', 
          'reported_at', 
          'location', 
          'duration', 
          'shape', 
          'description',
        ]
df_date_cols = ['sighted_at', 'reported_at']


def load_data() -> pd.DataFrame:
    ''' 
    Load data from Data/* into a pandas DataFrame

    Parameters
    ----------  
    how : specify the type of file to parse.
        'json' loads from the JSON file; 'tsv' loads from the TSV file

    '''
    try:  # attempt load with pd.read_json
        df = _simple_json_loader()
    except ValueError:
          # fallback to loopy implementation reader (filters out corrupt data)
        df = _default_json_loader()

    df[df_date_cols] = df[df_date_cols]\
                       .astype(str)\
                       .apply(
                            pd.to_datetime, errors='coerce', format='%Y%m%d'
                       )

    return df.reindex(columns=df_cols).replace('', pd.np.nan)


def _simple_json_loader() -> pd.DataFrame:
    '''
    Can be used once ufo_awesome.json has been corrected. 
    To fix the data, run `python3.6 fix_json_data.py`

    ''' 
    return pd.read_json('Data/ufo_awesome.json', lines=True)

def _default_json_loader() -> pd.DataFrame:
    '''
    Default imlementation, use when ufo_awesome.json contains malformed data.

    ''' 
    data = []
    with open('Data/ufo_awesome.json') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except ValueError:
                pass        # TODO fix buggy data

    return pd.DataFrame.from_records(data)


if __name__ == '__main__':
    df = load_data()
    print(df.head(3))
