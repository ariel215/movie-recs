import gensim.models.ldamodel as lda
from gensim.similarities import Similarity
from gensim.models.keyedvectors import Word2VecKeyedVectors as word2vec
from reviews.review_lda import EbertCorpus
import os
import numpy as np
import pandas as pd
import itertools
import num2words


class BadQueryError(Exception):
    pass


class Searcher(object):
    """
    A class for executing movie searches.
    """
    def __init__(self, config):
        self.config = config
        self.location = os.path.dirname(__file__)

    def _clean_query_word(self, qword):
        # turn decades into words
        decade = qword.rstrip("'s")
        if decade.isnumeric():
            return num2words.num2words(int(decade))

        else:
            return qword.lower()

    def clean_query(self, query_string):
        return [self._clean_query_word(qword)  for qs in query_string.split()
            for qword in qs.split('/')]

    def search(self, string):
        return self._search(self.clean_query(string))

    def _search(self, qlist):
        raise NotImplementedError

class LiteralSearcher(Searcher):

    def __init__(self,config):
        super(LiteralSearcher, self).__init__(config)
        sheet = pd.read_csv(os.path.join(self.location, 'data', config['tags']),
                            header=None)
        self.movie_list = sheet[0].values
        self.tags = sheet.iloc[:, 1:]

    def _search(self, query):

        match  = np.ones(self.movie_list.shape,bool)
        for term in query:
            match = match & (self.tags == term.strip()).any(axis=1).values

        return self.movie_list[match]


class TagSearcher(Searcher):

    def __init__(self, config):
        super(TagSearcher, self).__init__(config)

        self.sheet = pd.read_csv(os.path.join(self.location, 'data', config['tags']),
                            header=None, index_col=0)
        self.movie_list = self.sheet.index.values
        self.model = word2vec.load(
            os.path.join(os.path.dirname(__file__), 'data', 'word2vec.model')
        )
        self.tags = [self.fix_tags(r.dropna().to_list()) for _, r in self.sheet.iloc[:, 1:].iterrows()]

    def fix_tags(self, words: list):
        words = itertools.chain.from_iterable([x.lower().split() for x in words])
        words = itertools.chain.from_iterable([x.split('/') for x in words])
        return [w for w in words if w in self.model]

    def similarity(self, tags, query):
        qscores = [min(self.model.distance(q, t) for t in tags) for q in query]
        avg = np.linalg.norm(qscores, 4)
        return avg

    def _search(self, query):
        for q in query:
            if q not in self.model:
                raise BadQueryError(q)

        sims = [None for _ in self.tags]
        for i, row in enumerate(self.tags):
            try:
                similarity = self.similarity(
                        row, query)
                sims[i] = similarity
            except KeyError:
                print("Could not compute similarity for tag {}".format(row))
                sims[i] = +np.inf
        sim_idxs = np.argsort(sims)
        return self.movie_list[sim_idxs]


class LDASearcher(Searcher):

    def __init__(self, config):
        super(LDASearcher, self).__init__(config)

        self.model = lda.LdaModel.load(os.path.join(os.path.dirname(__file__),
                                                    'data', self.config['model']))
        self.corpus = EbertCorpus()
        self.sim_index = Similarity('sim', self.model[self.corpus], self.model.num_topics)

    def _search(self, query):
        bow = self.corpus.bag(self.corpus.bag(query))
        if len(bow) == 0:
            return []

        vec_query = self.model[bow]
        sims = self.sim_index[vec_query]
        sim_idxs = np.argsort(sims)
        names = [self.corpus.movie_names[x] for x in sim_idxs]
        return names


