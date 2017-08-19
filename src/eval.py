from sklearn.model_selection import cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score


class Evaluator:

    def __init__(self, pipeline, files, labels):
        self.pipeline = pipeline
        self.files = files
        self.labels = labels

    def evaluate(self, output=True):
        pass


class SplitEvaluator(Evaluator):

    def __init__(self, pipeline, files, labels, training_part):
        self.training_part = training_part
        super(SplitEvaluator, self).__init__(pipeline, files, labels)

    def evaluate(self, output=True):
        split_point = round(self.training_part*len(self.files))
        training_files, testing_files = self.files[:split_point], self.files[split_point:]
        training_labels, testing_labels = self.labels[:split_point], self.labels[split_point:]

        self.pipeline.fit(training_files, training_labels)
        pred = self.pipeline.predict(testing_files)

        precision = precision_score(testing_labels, pred, average='macro')
        recall = recall_score(testing_labels, pred, average='macro')
        f = f1_score(testing_labels, pred, average='macro')

        if output:
            print('Precision:\t{0}\nRecall:\t{1}\nF1:\t{2}'.format(precision, recall, f))


class NFoldEvaluator(Evaluator):

    def __init__(self, pipeline, files, labels, n=5):
        self.n = n
        super(NFoldEvaluator, self).__init__(pipeline, files, labels)

    def evaluate(self, output=True):
        scoring = cross_val_score(self.pipeline, self.files, self.labels, cv=self.n, scoring='f1_macro')

        if output:
            print('F1:\t{0}'.format(scoring.mean()))
