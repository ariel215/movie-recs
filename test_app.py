from unittest.mock import Mock, patch, MagicMock
from app.app import app_factory, application
import pytest

from app.model import Movie, Tag

@pytest.fixture
def client(small_index):
    application.index = small_index
    app = application.test_client()
    app.testing = True
    return app



def test_app_factory(small_index):
    config = {'TESTING': True}
    app = app_factory(config)
    assert app.testing

def test_main_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Movie Recommender -- Search" in response.data

def test_tagged_route(client):
    response = client.get('/tagged/action')
    assert response.status_code == 200
    assert b"Movie Recommender -- Tagged" in response.data

def test_tagged_route_404(client):
    response = client.get('/tagged/unknown')
    assert response.status_code == 404

def test_movie_route(client):
    response = client.get('/movies/The Matrix')
    assert response.status_code == 200
    assert b"Movie Recommender -- The Matrix" in response.data

@patch('app.app.application.index.movies')
def test_movie_route_404(mock_movies, client):
    mock_movies.get.return_value = None
    response = client.get('/movies/UnknownMovie')
    assert response.status_code == 404

def test_lucky_route(client):
    response = client.get('/lucky')
    assert response.status_code == 302
    assert b'/movies' in response.data

def test_show_all_route(client):
    response = client.get('/all')
    assert response.status_code == 200
    assert b"Movie Recommender -- Browse Movies" in response.data

@patch('app.app.application.search')
def test_search_route(mock_search, client):
    mock_search.return_value = [Mock(name="Movie1"), Mock(name="Movie2")]
    response = client.get('/search?search-query=test')
    assert response.status_code == 200
    assert b"Movie Recommender -- Results" in response.data
    mock_search.assert_called_with("test")
