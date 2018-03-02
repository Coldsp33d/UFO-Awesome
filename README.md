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

After this, ... >//<;

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

The starting point is a set of input files that have been aggregated to CSV (or JSON) from their original sources and formats.


This will clean all datasets and join them together.

-   The `Data/` folder contains all the data you will need to get up and running. It has subfolders `Input/` and `Resources/`, which contain input datasets, and various resources that are used for the join proces respectively.  
-   (to be continued...)

## Methodology

(Expand on this is need be)

(Repo and README curated with love by Shiva)
