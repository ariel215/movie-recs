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



@pytest.fixture
def full_index():
    csv_file = osp.join(ROOT, 'data', 'movie_tags.csv')
    return model.Index.from_csv(csv_file)


@pytest.fixture
def small_index():
    movies = [
        ['The Matrix', 'sci-fi', 'action', 'cyberpunk', '2000s', 'neo', 'keanu reeves'],
        ['Inception', 'sci-fi', 'action', 'mind-bending', '2010s', 'dream', 'leonardo dicaprio'],
        ['The Godfather', 'crime', 'drama', 'mafia', '1970s', 'don corleone', 'marlon brando'],
        ['Apocalypse Now', 'war', 'drama', 'vietnam war', '1970s', 'colonel kurtz', 'martin sheen', 'marlon brando'],
    ]
    return model.Index.from_lists(movies)


def test_from_lists(small_index):
    assert len(small_index.movies) == 4
    assert len(small_index.tags) > 0
    assert 'sci-fi' in small_index.tags
    assert 'drama' in small_index.tags
    assert 'action' in small_index.tags


def test_search_exact(small_index):

    results = small_index.search('drama')
    assert len(results) == 2
    assert all(any(tag.value == 'drama' for tag in movie.tags) for movie in results)

    results = small_index.search('nonexistent tag')
    assert len(results) == 0

    results = small_index.search('sci-fi action')
    assert len(results) == 2
    assert all(any(tag.value in ['sci-fi', 'action'] for tag in movie.tags) for movie in results)

    results = small_index.search('Marlon Brando drama')
    assert len(results) == 2
    result_names = {movie.name for movie in results}
    assert 'The Godfather' in result_names
    assert 'Apocalypse Now' in result_names

