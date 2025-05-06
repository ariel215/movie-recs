import flask
import os, json
from typing import List
import random
import app.model as model
from jinja2.filters import do_title

HERE = os.path.dirname(__file__)

class MyApp(flask.Flask):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(*args, **kwargs)
        self.index: model.Index = model.Index.from_csv(
            os.path.join(HERE, 'data', 'movie_tags.csv')
        )

    def search(self, string:str) -> List[model.SearchResult]:
        return self.index.search(string)

    def render_template(self, template, title, **kwargs):
        return flask.render_template(template, styles=[
            'style.css'
        ], title=title,
         **kwargs)


def app_factory(config) -> MyApp:
    _app = MyApp(__name__, instance_relative_config=True)
    _app.config.from_mapping(config)
    return _app


with open(os.path.join(
        os.path.dirname(__file__),
        'config.json'
)) as cfg_file:
    cfg = json.load(cfg_file)

application = app_factory(cfg)


@application.route('/')
def main():
    return application.render_template('home.html', title="Movie Recommender -- Search")


@application.route('/search')
def search():
    query = flask.request.args.get('search-query')
    movies = application.search(query)
    return application.render_template('search.html', "Movie Recommender -- Results",
                                       request=query,
                                       movies=movies)

@application.route('/tagged/<tag>')
def tagged(tag: str): 
    if tagged := application.index.tags.get(tag.lower()):
        return application.render_template(
            'tagged.html',
            "Movie Recommender -- Tagged",
            tag=tagged,
            movies=sorted(tagged.movies, key=lambda m: m.name)
        )
    else:
        return flask.Response(status=404)


@application.route('/movies/<name>')
def movie(name: str):
    movie = application.index.movies.get(name.lower())
    if movie:
        return application.render_template(
            'movie.html', 
            f'Movie Recommender -- {do_title(movie.name)}',
            movie=movie
        )
    else:
        return flask.Response(status=404)


@application.route('/lucky')
def lucky():
    movie = random.choice(list(application.index.movies.keys()))
    return flask.redirect(f'/movies/{movie}')


@application.route('/all')
def show_all():
    return application.render_template(
        'all.html', 'Movie Recommender -- Browse Movies',
        movies=sorted(application.index.movies.values(), key=lambda m: m.name)
    )
