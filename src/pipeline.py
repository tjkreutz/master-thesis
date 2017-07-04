import sys
import os
from math import ceil
from collections import defaultdict
from helpers.dataselection import *
from helpers.helperfunctions import *
from sklearn.svm import LinearSVC
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


FOLDS = 2


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


def train_test_binary_cls(pipeline, training_files, training_labels, test_files):

    pipeline.fit(training_files, training_labels)
    result = pipeline.predict(test_files)

    return result

def generate_binary_labels(datadir, label_dict):
    file_list = []
    binary_labels = defaultdict(list)
    line_index = 0
    for file, labels in label_dict.items():
        file_list.append(os.path.join(datadir, file))
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

    label_dict = read_labelfile(labelfile)
    label_predict_dict = defaultdict(list)

    file_list, binary_labels = generate_binary_labels(datadir, label_dict)
    pipeline = get_pipeline_configuration()

    files = [open(file, 'r').read() for file in file_list]
    cutoff = ceil(len(files) / FOLDS)

    scores = {'precision': [], 'recall': [], 'f1score': []}

    for i in range(FOLDS):
        starting_point = i * cutoff
        training_files = files[:starting_point] + files[starting_point+cutoff:]
        test_files = files[starting_point:starting_point+cutoff]
        test_file_list = file_list[starting_point:starting_point+cutoff]

        for label, values in binary_labels.items():

#            baseline = get_baseline(values)
#            print('Baseline accuracy for label {0}: {1}'.format(label, baseline))

            training_labels = values[:starting_point] + values[starting_point+cutoff:]
            results = train_test_binary_cls(pipeline, training_files, training_labels, test_files)

            for r in range(len(results)):
                if results[r]:
                    filename = os.path.basename(test_file_list[r])
                    label_predict_dict[filename].append(label)

        precision, recall, f1score = evaluate_from_dict(label_dict, label_predict_dict)
        scores['precision'].append(precision)
        scores['recall'].append(recall)
        scores['f1score'].append(f1score)

    for score in scores:
        print('Average {0}: {1}'.format(score, sum(scores[score])/len(scores[score])))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])