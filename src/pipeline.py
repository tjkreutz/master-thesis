import sys
import os
import numpy as np
from features import *
from util import read_labelfile
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import CountVectorizer


def get_pipeline_configuration():

    clf = DecisionTreeClassifier()
    pipeline = Pipeline([
        ('features', FeatureUnion([
#            ('countadjectives', CountAdjectives()),
#            ('taggedwords', TaggedWords()),
#            ('skipgrams', SkipgramVectorizer(n=3, k=2, max_df=0.9)),
            ('countvectorizer', CountVectorizer(ngram_range=(1, 1), max_df=0.9)),
#            ('documentlength', DocumentLength()),
#            ('typetokenratio', TypeTokenRatio()),
#            ('numberofparagraphs', NumberOfParagraphs()),
#            ('rechtbank', Rechtbank()),
        ])),
        ('classifier', clf)
    ])

    return pipeline


def show_plot(clf, training_features, training_labels, testing_features, testing_labels):
    # Plotting decision regions

    importances = clf.feature_importances_

    indices = np.argsort(importances)[::-1]
    used_features = indices[:2]

    two_training_features = training_features[:, used_features].todense()
    two_testing_features = testing_features[:, used_features].todense()

    clf = DecisionTreeClassifier()
    clf.fit(two_training_features, training_labels)

    x_min, x_max = two_training_features[:, 0].min() - 1, two_training_features[:, 0].max() + 1
    y_min, y_max = two_training_features[:, 1].min() - 1, two_training_features[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ar = plt.subplot()

    ar.scatter(two_testing_features[:, 0], two_testing_features[:, 1], c=testing_labels, s=20, edgecolor='k')
    ar.contourf(xx, yy, Z, alpha=0.4)

    plt.show()


def main(datadir):

    if not os.path.isfile(os.path.join(datadir, 'labelfile.csv')):
        print('Labelfile not found in {}'.format(datadir))
        exit(0)
    labelfile = open(os.path.join(datadir, 'labelfile.csv'), 'r')

    label_dict = read_labelfile(labelfile)
    files = []
    labels = []

    for filename, labelset in label_dict.items():
        files.append(open(os.path.join(datadir, filename), 'r', encoding='utf-8').read())
        labels.append(labelset)

    mlb = MultiLabelBinarizer()
    labels = mlb.fit_transform(labels)
#    print(mlb.classes_)
    newlabels = [0] * len(labels)
    for l in range(len(labels)):
        newlabels[l] = labels[l][3]

    vec = CountVectorizer(ngram_range=(1, 1), max_df=0.9)
    clf = DecisionTreeClassifier()

    split = round(0.75*len(files))
    training_files, testing_files = files[:split], files[split:]
    training_labels, testing_labels = newlabels[:split], newlabels[split:]

    training_features = vec.fit_transform(training_files)
    testing_features = vec.transform(testing_files)
    clf.fit(training_features, training_labels)

    pred = clf.predict(testing_features)
    print('Precision:\t{0}\nRecall:\t{1}\nF1:\t{2}'.format(
        precision_score(testing_labels, pred),
        recall_score(testing_labels, pred),
        f1_score(testing_labels, pred)))

    show_plot(clf, training_features, training_labels, testing_features, testing_labels)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])