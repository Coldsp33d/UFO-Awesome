#!/usr/bin/env python2.7
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

# Computing pairwise jaccard similarity for a given directory of files

from tika import parser
import os, itertools, argparse, csv

def filterRows(inputCSV, featureSet):
    data_rows = []
    reader = csv.DictReader(open(inputCSV, 'rb'))
    for line in reader:
        line = {feature_key: float(line[feature_key]) for feature_key in featureSet}
        data_rows.append(line)
    return data_rows


def computeScores(inputCSV, outCSV, featureSet):

    with open(outCSV, "wb") as outF:
      a = csv.writer(outF, delimiter=',')
      a.writerow(["x-coordinate","y-coordinate","Similarity_score"])

      data_tuple = itertools.combinations(filterRows(inputCSV, featureSet), 2)

      for data1, data2 in data_tuple:

        isCoExistant = lambda k: ( k in data2) and ( data1[k] == data2[k] )
        intersection = reduce(lambda m,k: (m + 1) if isCoExistant(k) else m, data1.keys(), 0)


        union = len(data1.keys()) + len(data2.keys()) - intersection
        jaccard = float(intersection) / union

        a.writerow([data1, data2, jaccard])


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputCSV', required=True, help='path to input file containing data to be compared')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Jaccard similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity specified header columns in CSV')
    args = argParser.parse_args()

    if args.inputCSV and args.outCSV:
        computeScores(args.inputCSV, args.outCSV, args.accept)
