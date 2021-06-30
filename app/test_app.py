from recommender.model import LDASearcher, TagSearcher, LiteralSearcher
import pytest
from . import app
import jinja2, flask


@pytest.fixture
def lda_cfg():
    return {'model': 'ebert.lda'}

@pytest.fixture
def tag_cfg():
    return {'tags': 'movie_tags.csv'}

@pytest.fixture()
def webapp(tag_cfg):
    return app.application.test_client()

@pytest.mark.searcher
@pytest.mark.skip
def test_lda(lda_cfg):
    searcher = LDASearcher(lda_cfg)
    names = searcher.search("aliens")
    print(names[:5])

@pytest.mark.searcher
def test_tags(tag_cfg):
    searcher = TagSearcher(tag_cfg)
    for query in ["horror", "80's horror", "World War II", "Jewish"]:
        print("Search: {}".format(query))
        print(searcher.search(query)[:5])


@pytest.mark.searcher
def test_literals(tag_cfg):
    searcher = LiteralSearcher(tag_cfg)
    names = searcher.search("Sports")
    print(names[:5])


@pytest.mark.app
def test_home(webapp):
    assert '200' in webapp.get('/').status


@pytest.mark.app
def test_search(webapp):
    response = webapp.get('/search?search-query=war')
    assert '200' in response.status

@pytest.mark.app
@pytest.mark.parametrize(
    'movie_name', ['Miracle', 'Eighth Grade',
                   'Yours, Mine and Ours (2005)']
)
def test_movie(webapp, movie_name):
    response = webapp.get(f'/movies/{jinja2.filters.do_urlencode(movie_name)}')
    assert '200' in response.status


@pytest.mark.app
def test_lucky(webapp):
    assert '302' in webapp.get('/lucky').status


@pytest.mark.app
def test_show_all(webapp):
    assert '200' in webapp.get('/all').status



if __name__ == "__main__":
    cfg = {'tags': 'movie_tags.csv'}
    searcher = TagSearcher(cfg)
    input("press any key to continue")