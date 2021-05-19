from recommender.model import LDASearcher, TagSearcher, LiteralSearcher
from pytest import mark, fixture
import jinja2

@mark("searcher")
def test_lda():
    cfg = {'model': 'ebert.lda'}
    searcher = LDASearcher(cfg)
    names = searcher.search("aliens")
    print(names[:5])


@mark("searcher")
def test_tags():
    cfg = {'tags': 'movie_tags.csv'}
    searcher = TagSearcher(cfg)
    for query in ["horror", "80's horror", "World War II", "Jewish"]:
        print("Search: {}".format(query))
        print(searcher.search(query)[:5])


@mark("searcher")
def test_literals():
    cfg  = {'tags': 'movie_tags.csv'}
    searcher = LiteralSearcher(cfg)
    names = searcher.search("Sports")

    print(names)
