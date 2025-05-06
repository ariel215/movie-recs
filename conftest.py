import pytest
import os.path as osp
from app import model

ROOT = osp.dirname(model.__file__)


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
