import sys
import os
from collections import defaultdict
from helpers.dataselection import *
from sklearn.svm import LinearSVC
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


def train_binary_cls(file_list, labels):

    training_files = [open(file, 'r').read() for file in file_list]

    pipeline = Pipeline([
            ('features', FeatureUnion([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 1))),
            ])),
            ('classifier', LinearSVC())
    ])

    pipeline.fit_transform(training_files, labels)
    return pipeline


def generate_binary_labels(labelfile):
    file_list = []
    binary_labels = defaultdict(list)
    line_index = 0
    for line in labelfile.readlines():
        file, labels = line.split('\t')
        file_list.append(file)
        labels = [label.strip() for label in labels.split(',')]
        for label in labels:
            index_diff = line_index - len(binary_labels[label])
            if index_diff:
                binary_labels[label].extend([0]*index_diff)
            binary_labels[label].append(1)
        line_index += 1

    for label, values in binary_labels.items():
        if len(file_list) > len(values):
            binary_labels[label].extend([0] * (len(file_list) - len(values)))

    return file_list, binary_labels


def main(datadir):

    if not os.path.isfile(os.path.join(datadir, 'labelfile.csv')):
        print('Labelfile not found in {}'.format(datadir))
        exit(0)

    labelfile = open(os.path.join(datadir, 'labelfile.csv'), 'r')

    file_list, binary_labels = generate_binary_labels(labelfile)

    for labels in binary_labels.items():
        train_binary_cls(file_list, labels)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])