from app import model
import os.path as osp
import pytest

ROOT = osp.dirname(model.__file__)

def test_from_csv():
    csv_file = osp.join(ROOT, 'data', 'movie_tags.csv')
    index = model.Index.from_csv(
        csv_file
    )
    assert len(index.movies) == len(open(csv_file, encoding='utf8').readlines())



def test_from_lists(small_index):
    assert len(small_index.movies) == 4
    assert len(small_index.tags) > 0
    assert 'sci-fi' in small_index.tags
    assert 'drama' in small_index.tags
    assert 'action' in small_index.tags


def test_search_exact(small_index):

    results = small_index.search('drama')
    assert len(results) == 2
    assert all(any(tag.value == 'drama' for tag in result.movie.tags) for result in results)

    results = small_index.search('nonexistent tag')
    assert len(results) == 0

    results = small_index.search('sci-fi action')
    assert len(results) == 2
    for result in results:
        assert any(tag.value == 'sci-fi' for tag in result.movie.tags)
        assert any(tag.value == 'action' for tag in result.movie.tags)


    results = small_index.search('Marlon Brando drama')
    assert len(results) == 2
    result_names = {result.movie.name for result in results}
    assert 'The Godfather' in result_names
    assert 'Apocalypse Now' in result_names

    results = small_index.search('sci-fi cyberpunk')
    assert len(results) == 1
    assert results[0].movie.name == 'The Matrix'

def test_search_partial_names(small_index: model.Index):
    assert small_index.search('godfather')[0].movie.name == 'The Godfather'
    assert small_index.search('apocalypse')[0].movie.name == 'Apocalypse Now'


def test_search_partial_tags(small_index: model.Index):
    results = small_index.search('cyberpunk war')
    movie_names = [result.movie.name for result in results]
    assert 'The Matrix' in movie_names
    assert 'Apocalypse Now' in movie_names