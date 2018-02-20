"""
Utility for converting one file format to another
Like from CSV to JSON
Can be extended to add methods to convert XML to JSON
"""

import csv
import json


def convert_csv_to_json(csv_file_location, json_file_location):
    """
    Usage: convert_csv_to_json('data/airport-codes.csv', 'data/airport-codes.json')
    """
    csv_file = open(csv_file_location, 'r', encoding='utf8')
    json_file = open(json_file_location, 'w', encoding='utf8')
    reader = csv.reader(csv_file)
    csv_headers = next(reader)
    dict_reader = csv.DictReader(csv_file, csv_headers)
    for row in dict_reader:
        json.dump(row, json_file)
        json_file.write('\n')
    csv_file.close()
    json_file.close()