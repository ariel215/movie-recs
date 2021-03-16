import gensim.models.ldamodel as lda
from gensim.similarities import Similarity
import gensim.downloader as api
from reviews.review_lda import EbertCorpus
import os
import numpy as np
import pandas as pd
import itertools


class Searcher(object):
    """
    A class for executing movie searches.
    """
    def __init__(self, config):
        self.config = config
        self.location = os.path.dirname(__file__)

    def search(self, string):
        raise NotImplementedError


class LiteralSearcher(Searcher):

    def __init__(self,config):
        super(LiteralSearcher, self).__init__(config)
        sheet = pd.read_csv(os.path.join(self.location, 'data', config['tags']),
                            header=None)
        self.movie_list = sheet[0].values
        self.tags = sheet.iloc[:, 1:]

    def search(self,string_):

        query = string_.split()
        match  = np.ones(self.movie_list.shape,bool)
        for term in query:
            match = match & (self.tags == term.strip()).any(axis=1).values

        return self.movie_list[match]


class TagSearcher(Searcher):

    def __init__(self, config):
        super(TagSearcher, self).__init__(config)

        sheet = pd.read_csv(os.path.join(self.location,'data',config['tags']),
                            header=None)
        self.movie_list = sheet[0].values
        self.tags = sheet.iloc[:, 1:]
        self.model = api.load('glove-wiki-gigaword-50')

    @staticmethod
    def fix_tags(words: list):
        words = itertools.chain.from_iterable([x.lower().split() for x in words])
        words = itertools.chain.from_iterable([x.split('/') for x in words])
        return list(words)

    def search(self, string):
        query = [EbertCorpus.preprocess(s) for s in string.split()]
        sims = [None for _ in self.tags.iterrows()]
        for i, row in self.tags.iterrows():
            try:
                similarity = self.model.n_similarity(
                        self.fix_tags(row.dropna().tolist()),
                        query)
                sims[i] = similarity
            except KeyError:
                print("Could not compute similarity for row %d"%i)
                sims[i] = -np.inf
        sim_idxs = np.argsort(sims)
        return self.movie_list[sim_idxs]


class LDASearcher(Searcher):

    def __init__(self, config):
        super(LDASearcher, self).__init__(config)

        self.model = lda.LdaModel.load(os.path.join(os.path.dirname(__file__),
                                                    'data', self.config['model']))
        self.corpus = EbertCorpus()
        self.sim_index = Similarity('sim', self.model[self.corpus], self.model.num_topics)

    def search(self, string):
        query = EbertCorpus.preprocess([s for s in string.split()])
        bow = self.corpus.bag(self.corpus.bag(query))
        if len(bow) == 0:
            return []

        vec_query = self.model[bow]
        sims = self.sim_index[vec_query]
        sim_idxs = np.argsort(sims)
        names = [self.corpus.movie_names[x] for x in sim_idxs]
        return names


