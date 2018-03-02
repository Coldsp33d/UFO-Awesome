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

import editdistance, itertools, argparse, csv


def stringify(attribute_value):
    if isinstance(attribute_value, list):
        return str((", ".join(attribute_value)).encode('utf-8').strip())
    else:
        return str(attribute_value.encode('utf-8').strip())


def filterRows(inputCSV, featureSet, label):
    data_rows = []
    reader = csv.DictReader(open(inputCSV, 'r'))
    for line in reader:
        if featureSet == None:
            featureSet = list(line.keys())
        featureSet.append(label)
        line = {feature_key: line[feature_key] for feature_key in featureSet}
        data_rows.append(line)
    return data_rows

def computeScores(inputCSV, outCSV, label, acceptTypes, allKeys):
    with open(outCSV, "w", newline='') as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        data_tuple = itertools.combinations(filterRows(inputCSV, acceptTypes, label), 2)
        for data1, data2 in data_tuple:
            try:
                row_edit_distance = [data1[label], data2[label]]
                data1_copy = data1.copy()
                data1_copy.pop(label, None)

                data2_copy = data2.copy()
                data2_copy.pop(label, None)

                file1_parsedData = list(data1_copy.keys())
                file2_parsedData = list(data2_copy.keys())

                intersect_features = set(file1_parsedData) & set(file2_parsedData)

                file_edit_distance = 0.0
                for feature in intersect_features:

                    file1_feature_value = stringify(data1[feature])
                    file2_feature_value = stringify(data2[feature])

                    if len(file1_feature_value) == 0 and len(file2_feature_value) == 0:
                        feature_distance = 0.0
                    else:
                        feature_distance = float(editdistance.eval(file1_feature_value, file2_feature_value)) / (
                        len(file1_feature_value) if len(file1_feature_value) > len(file2_feature_value) else len(
                            file2_feature_value))

                    file_edit_distance += feature_distance

                if allKeys:
                    file1_only_features = set(file1_parsedData) - set(intersect_features)

                    file2_only_features = set(file2_parsedData) - set(intersect_features)

                    file_edit_distance += len(file1_only_features) + len(
                        file2_only_features)  # increment by 1 for each disjunct feature in (A-B) & (B-A), file1_disjunct_feature_value/file1_disjunct_feature_value = 1
                    file_edit_distance /= float(
                        len(intersect_features) + len(file1_only_features) + len(file2_only_features))

                else:
                    file_edit_distance /= float(len(intersect_features))  # average edit distance

                row_edit_distance.append(1 - file_edit_distance)
                a.writerow(row_edit_distance)

            except KeyError:
                continue


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Edit Distance Similarity based on Metadata values')
    argParser.add_argument('--inputCSV', required=False, help='path to input file containing data to be compared')
    argParser.add_argument('--outCSV', required=True,
                           help='path to directory for storing the output CSV File, containing pair-wise Similarity Scores based on edit distance')
    argParser.add_argument('--label', required=True,
                           help='label that should appear on the graphs')
    argParser.add_argument('--accept', nargs='+', type=str,
                           help='Optional: compute similarity only on specified IANA MIME Type(s)')
    argParser.add_argument('--allKeys', action='store_true', help='compute edit distance across all keys')
    args = argParser.parse_args()

    if args.inputCSV and args.outCSV:
        computeScores(args.inputCSV, args.outCSV, args.label, args.accept, args.allKeys)