from nltk.corpus import alpino
from nltk.util import skipgrams
from nltk.tag import PerceptronTagger
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer


class CountAdjectives(TransformerMixin):
    """ adds postags, learns weights """

    def __init__(self):
        super(CountAdjectives, self).__init__()
        self.tagger = PerceptronTagger(load=True)
        training_corpus = list(alpino.tagged_sents())
        self.tagger.train(training_corpus)

    def postag(self, x):
        postagged = self.tagger.tag(x.split())
        onlytags = [tt[1] for tt in postagged]
        return onlytags

    def count_adjectives(self, x):
        postagged = self.postag(x)
        totalcount = len(postagged)
        adjlength = postagged.count('adj')
        if adjlength > 0:
            return adjlength/totalcount
        return 0

    def transform(self, X, y=None):
        new_X = [[self.count_adjectives(x)] for x in X]
        return new_X

    def fit(self, X, y=None):
        return self


class SkipgramVectorizer(TfidfVectorizer):
    """ Learns weights for skipgrams """

    def __init__(self, n=2, k=2, **kwargs):
        super(SkipgramVectorizer, self).__init__(**kwargs)
        self.n = n
        self.k = k

    def generate_skipgrams(self, x):
        return skipgrams(x.split(), n=self.n, k=self.k)

    def build_analyzer(self):
        return self.generate_skipgrams


class TaggedWords(TransformerMixin):
    """outputs average word length per document"""

    def tagged_words(self, x):
        record = False
        tokens = x.split()
        vec = [0, 0, 0, 0, 0, 0, 0, 0]
        tag_words = ['verdachte', 'nummer', 'naam', 'bedrijf', 'adres', 'slachtoffer', 'aangever', 'kenteken']
        for token in tokens:
            if record == True:
                token = token.strip().lower()
                if token in tag_words:
                    vec[tag_words.index(token)] += 1
                record = False
            if token == '[':
                record = True

        return vec

    def transform(self, X, y=None):
        return [self.tagged_words(x) for x in X]

    def fit(self, X, y=None):
        return self


class DocumentLength(TransformerMixin):
    """outputs average word length per document"""

    def document_length(self, x):
        return len(x.split())

    def transform(self, X, y=None):
        return [[self.document_length(x)] for x in X]

    def fit(self, X, y=None):
        return self


class TypeTokenRatio(TransformerMixin):
    """outputs average word length per document"""

    def type_token_ratio(self, x):
        tokens = x.split()
        types = set()
        for word in tokens:
            types.add(word.lower())
        return len(types)/len(tokens)

    def transform(self, X, y=None):
        return [[self.type_token_ratio(x)] for x in X]

    def fit(self, X, y=None):
        return self


class NumberOfParagraphs(TransformerMixin):
    """outputs average word length per document"""

    def number_of_paragraphs(self, x):
        paragraphs = 0
        lines = x.split('\n')
        for line in lines:
            if len(line) < 6:
                paragraphs += 1
        return paragraphs

    def transform(self, X, y=None):
        return [[self.number_of_paragraphs(x)] for x in X]

    def fit(self, X, y=None):
        return self


class Rechtbank(TransformerMixin):
    """outputs average word length per document"""

    def rechtbank(self, x):
        rechtbanken = ['rechtbank amsterdam',
                       'rechtbank den haag',
                       'rechtbank gelderland',
                       'rechtbank limburg',
                       'rechtbank midden-nederland',
                       'rechtbank noord-holland',
                       'rechtbank noord-nederland',
                       'rechtbank oost-brabant',
                       'rechtbank overijssel',
                       'rechtbank rotterdam',
                       'rechtbank zeeland-west-brabant']
        lines = x.split('\n')
        if lines[0].lower() in rechtbanken:
            return rechtbanken.index(lines[0].lower())
        return 0

    def transform(self, X, y=None):
        return [[self.rechtbank(x)] for x in X]

    def fit(self, X, y=None):
        return self