from sklearn.base import TransformerMixin


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