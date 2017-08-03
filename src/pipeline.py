import sys
import os
from util import read_labelfile
from features import *
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import CountVectorizer


def get_pipeline_configuration():

    clf = OneVsRestClassifier(DecisionTreeClassifier())
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('countvectorizer', CountVectorizer(ngram_range=(1, 1), max_df=0.9)),
            ('documentlength', DocumentLength()),
            ('typetokenratio', TypeTokenRatio()),
            ('numberofparagraphs', NumberOfParagraphs()),
            ('rechtbank', Rechtbank()),
        ])),
        ('classifier', clf)
    ])

    return pipeline


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

    labels = MultiLabelBinarizer().fit_transform(labels)

    pipeline = get_pipeline_configuration()
    scores = cross_val_score(pipeline, files, labels, cv=2, scoring='f1_samples')
    print(scores.mean())


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])