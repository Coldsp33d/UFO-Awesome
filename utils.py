import json
import pandas as pd

def load_data(how: str = 'json') -> pd.DataFrame:
    """ 
    Load data from Data/* into a pandas DataFrame

    Parameters
    ----------  
    how : specify the type of file to parse.
        'json' loads from the JSON file, or 'tsv' to load from the TSV
    """

    if how == 'json':
        data = []
        with open('Data/ufo_awesome.json') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except ValueError:
                    pass        # TODO fix buggy data

        return pd.DataFrame.from_records(data)

    # TODO implement how='tsv'

if __name__ == '__main__':
    df = load_data()
    print(df.head(3))
