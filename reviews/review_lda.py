import os,glob

from gensim.corpora import dictionary
import gensim.models.lsimodel as lsi
import gensim.models.ldamodel as lda
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS as gensim_stopwords
import nltk



class EbertCorpus(object):
    _stemmer = nltk.stem.SnowballStemmer("english")
    _lemmatizer = nltk.stem.WordNetLemmatizer()

    def __init__(self):
        review_dir = os.path.join(os.path.dirname(__file__), 'ebert')
        self.review_names = glob.glob(os.path.join(review_dir, '*review.txt'))
        self.movie_names = [os.path.basename(name).rpartition('_')[0] for name in self.review_names]
        self.dictionary = dictionary.Dictionary(doc for doc in self.text())
        self.dictionary.filter_extremes(no_below=15, no_above=0.35)

    def text(self):
        for name in self.review_names:
            with open(name) as rf:
                words = [self.preprocess(word) for word in simple_preprocess(rf.read(), deacc=True)
                         if word not in gensim_stopwords]
                yield words

    @classmethod
    def preprocess(cls,word):
        return cls._stemmer.stem(cls._lemmatizer.lemmatize(word))

    def __iter__(self):
        for doc in self.text():
            yield self.dictionary.doc2bow(doc)

    def bag(self, doc):
        return self.dictionary.doc2bow([self.preprocess(wrd) for wrd in doc])


if __name__ == "__main__":

    corpus = EbertCorpus()
    mdl = lsi.LsiModel(corpus, num_topics=25, id2word=corpus.dictionary,)
    mdl.save('ebert.lsi')
    topics = mdl.print_topics(-1)
    with open('ebert_topics.csv', 'w') as topic_list:
        for topic in topics:
            topic_list.write("{},{}\n".format(topic[0], topic[1]))
