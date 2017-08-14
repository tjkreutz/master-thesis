import sys
import os
from features import *
from util import read_labelfile
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import AdaBoostClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import CountVectorizer


def get_pipeline_configuration():

    clf = OneVsRestClassifier(AdaBoostClassifier())
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
    split = round(0.75*len(files))
    training_files, testing_files = files[:split], files[split:]
    training_labels, testing_labels = labels[:split], labels[split:]

    pipeline.fit(training_files, training_labels)
    pred = pipeline.predict(testing_files)

    print('Precision:\t{0}\nRecall:\t{1}\nF1:\t{2}'.format(
        precision_score(testing_labels, pred, average='macro'),
        recall_score(testing_labels, pred, average='macro'),
        f1_score(testing_labels, pred, average='macro')))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])