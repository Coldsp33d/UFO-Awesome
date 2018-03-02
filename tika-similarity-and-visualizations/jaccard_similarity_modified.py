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
from functools import reduce

def filterRows(inputCSV, featureSet, label):
    data_rows = []
    reader = csv.DictReader(open(inputCSV, 'r'))
    for line in reader:
        if featureSet is None:
            featureSet = list(line.keys())
        featureSet.append(label)
        line = {feature_key: line[feature_key] for feature_key in featureSet}
        data_rows.append(line)
    return data_rows


def computeScores(inputCSV, outCSV, label, featureSet):

    with open(outCSV, "w", newline='') as outF:
      a = csv.writer(outF, delimiter=',')
      a.writerow(["x-coordinate","y-coordinate","Similarity_score"])

      data_tuple = itertools.combinations(filterRows(inputCSV, featureSet, label), 2)


      for data1, data2 in data_tuple:
        data1_copy = data1.copy()
        data1_copy.pop(label, None)
        data1_copy = {k: float(v) for k, v in data1_copy.items()}

        data2_copy = data2.copy()
        data2_copy.pop(label, None)
        data2_copy = {k: float(v) for k, v in data2_copy.items()}

        isCoExistant = lambda k: ( k in data2_copy) and ( data1_copy[k] == data2_copy[k] )
        intersection = reduce(lambda m,k: (m + 1) if isCoExistant(k) else m, data1_copy.keys(), 0)


        union = len(data1_copy.keys()) + len(data2_copy.keys()) - intersection
        jaccard = float(intersection) / union

        a.writerow([data1[label], data2[label], jaccard])


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputCSV', required=True, help='path to input file containing data to be compared')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Jaccard similarity Scores')
    argParser.add_argument('--label', required=True,
                           help='label that should appear on the graphs')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity specified header columns in CSV')
    args = argParser.parse_args()

    if args.inputCSV and args.outCSV:
        computeScores(args.inputCSV, args.outCSV, args.label, args.accept)