import utils
import pandas as pd
import json

from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
import os

# list of words in the english dictionary
# used as a replacement for spell checking which would've been an extremely time consuming operation
words = set(
            pd.read_csv(
                    'Data/Resources/words.txt', 
                    header=None, 
                    squeeze=True
            )
            .str.strip()
            .tolist()
)

# custom storword list - more comprehensive than NLTK's set
stopwords = set(  
                pd.read_csv(
                        'Data/Resources/stopwords.txt', 
                        header=None, 
                        squeeze=True
                )
                .str.strip()
                .tolist()
).union(['&quot','w/','&amp','&apos','quot'])


lemmatizer = WordNetLemmatizer()

def preprocess(x : str) -> str:
    ''' 
    NLTK-based cleaning:
        1.  Stopword removal
        2.  Invalid word removal
        3.  Lemmatization
    ''' 
    x = [
            lemmatizer.lemmatize(w) for w in x.split() 
                    if w in words and w not in stopwords
    ]                                                      # remove stopwords
    return ' '.join(x)                                     # join the list

if __name__ == '__main__':
    df = utils.simple_csv_loader(
            'Data/ufo_awesome_joined.csv', 
            usecols=['description', 'state'], 
            compression='gzip', 
    )

    df.description = df.description.apply(preprocess)      # stopword removal done HERE

    v = df.groupby(
            df.state, 
            as_index=False, 
            squeeze=True
        ).description.apply(' '.join)

    # with love from https://stackoverflow.com/q/34232190/4909087
    tfidf = TfidfVectorizer(use_idf=True) 
    X = tfidf.fit_transform(v).nonzero()[1]   # transformed counts
    f = pd.np.array(tfidf.get_feature_names())   # feature names 

    json.dump(f[X[:100]].tolist(), open('Data/Resources/keywords.json', 'w'))


    

