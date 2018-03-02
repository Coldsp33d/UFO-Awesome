# Content Detection Assignment - 1 - 

Featuring the *[UFO Awesome dataset](https://www.dropbox.com/sh/s1lgh3fjtc5d12x/AADZUx0SVmBmw76SYeMylF2Sa?dl=0).*

## Team Members

1.  Akashdeep Singh
2.  Koustav Mukherjee
3.  Sayali Ghaisas
4.  Shiva Deviah
5.  Vritti Rohira

## Getting Started

This project was written in `python-3.6`. To install all required modules, please run

    pip install --upgrade -r requirements.txt 

To get started, first run a script to clean all input datasets and join them with the *UFO Awesome* dataset. All input files (including the `ufo_awesome.json` UFO data) are located in `Data/Input/`.

    python datajoiner.py

This generates a CSV file `Data/ufo_awesome_joined.csv` with 61K rows and 29 features. The CSV is `gzip` compressed using pandas, so it cannot be read by excel directly. If you want to peek into the data, fire up an interpreter and run the following code:

    In [1]: import utils

    In [2]: df = utils.simple_csv_loader(
       ...:         'Data/ufo_awesome_joined.csv', 
       ...:         parse_dates=utils.df_date_cols, 
       ...:         compression='gzip'
       ...: )

    In [3]: df.head()

After this, you can then run some queries to generate vizualizations. First, run 

    python queries.py

This generates some CSV files in `Data/Viz/` that are used as input to the Tika visualization code. After this, cd into the `tika-similarity-and-visualizations\` folder, and run any of the following script(s):

    python cosine_similarity_modified.py --inputCSV ../Data/Viz/census_2000.csv --outCSV ../Data/Viz/census_2000_out.csv --label shape

This performs cosine similarity. Alternatively, for edit distance, run:

    python3.6 edit-value-similarity-modified.py --inputCSV ../Data/Viz/census_2000.csv --outCSV ../Data/Viz/census_2000_out.csv --label shape

Alternatively, for Jaccard similarity, run:

    python jaccard_similarity_modified --inputCSV ../Data/Viz/census_2000.csv --outCSV ../Data/Viz/census_2000_out.csv --label shape


Next, to view the graphs on your browser, start localhost, and then, run any of the following:

    python edit-cosine-circle-packing.py --inputCSV ../Data/Viz/census_2000_out.csv --cluster 0

And then open `circlepacking.html` to see a circlepacking graph. Or,

    python edit-cosine-correlation-matrix.py --inputCSV ../Data/Viz/census_2000_out.csv

And then open `correlation-matrix-d3.html` in a browser to see a correlation matrix. Or,

    python edit-cosine-cluster.py --inputCSV ../Data/Viz/census_2000_out.csv --cluster 0

And then open `cluster-d3.html` to see a Dendrogram.

## Project structure

    \
    ├── Data
    │   ├── Input
    │   │   ├── ...
    │   └── Resources
    │       └── ...
    ├── datacleaner.py
    ├── datajoiner.py
    ├── fix_json_data.py
    ├── geocode.py
    ├── geocode_mp.py
    ├── keyword_extraction.py
    ├── requirements.txt
    ├── tika-similarity-and-visualizations
    │   └── ...
    └── utils.py


(Repo and README curated with love by Shiva)
