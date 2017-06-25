import sys
import os
from collections import defaultdict
from helpers.dataselection import *
from sklearn.svm import LinearSVC
from sklearn.cross_validation import cross_val_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


def get_pipeline_configuration():

    clf = LinearSVC()
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 1))),
        ])),
        ('classifier', clf)
    ])

    return pipeline


def get_baseline(labels):
    return max(labels.count(0), labels.count(1)) / len(labels)


def train_test_binary_cls(pipeline, file_list, labels):

    training_files = [open(file, 'r').read() for file in file_list]
    scores = cross_val_score(pipeline, training_files, labels)

    return scores


def generate_binary_labels(datadir, labelfile):
    file_list = []
    binary_labels = defaultdict(list)
    line_index = 0
    for line in labelfile.readlines():
        file, labels = line.split('\t')
        file_list.append(os.path.join(datadir, file))
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

    file_list, binary_labels = generate_binary_labels(datadir, labelfile)
    pipeline = get_pipeline_configuration()

    for label, values in binary_labels.items():
        baseline = get_baseline(values)
        print('Baseline accuracy for label {0}: {1}'.format(label, baseline))
        scores = train_test_binary_cls(pipeline, file_list, values)
        print('Crossvalidation accuracy for label {0}: {1}'.format(label, scores.mean()))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])