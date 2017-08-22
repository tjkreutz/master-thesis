import sys
import os
from eval import *
from features import *
from util import read_labelfile
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import CountVectorizer


def get_pipeline_configuration():

    clf = OneVsRestClassifier(DecisionTreeClassifier())
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('countadjectives', CountAdjectives()),
            ('taggedwords', TaggedWords()),
            ('skipgrams', SkipgramVectorizer(n=2, k=2, max_df=0.9)),
            ('countvectorizer', CountVectorizer(ngram_range=(1, 3), max_df=0.4, input='filename')),
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
    evaluator = NFoldEvaluator(pipeline, files, labels, 5)
    evaluator.evaluate()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])