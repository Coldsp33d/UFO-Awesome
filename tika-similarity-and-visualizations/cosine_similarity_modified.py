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

from vector import Vector
import itertools, argparse, csv


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
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        data_tuple = itertools.combinations(filterRows(inputCSV, featureSet), 2)
        for data1, data2 in data_tuple:
            try:
                row_cosine_distance = ['_'.join(map(str,data1.values())), '_'.join(map(str,data2.values()))]
                v1 = Vector()
                v1.features = data1
                v2 = Vector()
                v2.features = data2

                row_cosine_distance.append(v1.cosTheta(v2))

                a.writerow(row_cosine_distance)
            except KeyError:
                continue


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Cosine similarity based on Metadata values')
    argParser.add_argument('--inputCSV', required=True, help='path to input file containing data to be compared')
    argParser.add_argument('--outCSV', required=True,
                           help='path to directory for storing the output CSV File, containing pair-wise Cosine similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str,
                           help='Optional: compute similarity only on specified header columns in CSV')
    args = argParser.parse_args()

    if args.inputCSV and args.outCSV:
        computeScores(args.inputCSV, args.outCSV, args.accept)