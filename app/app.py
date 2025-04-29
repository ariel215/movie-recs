import flask
import os, json
from typing import List, Optional
from pandas import DataFrame
import random
import model

HERE = os.path.dirname(__file__)

class MyApp(flask.Flask):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(*args, **kwargs)
        self.index: model.Index = model.Index.from_csv(
            os.path.join(HERE, 'data', 'movie_tags.csv')
        )

    def search(self, string) -> List[str]:
        return self.index.search(string)

    def render_template(self, template, title, **kwargs):
        return flask.render_template(template, styles=[
            'style.css'
        ], title=title,
         **kwargs)


def app_factory(config):
    _app = MyApp(__name__, instance_relative_config=True)
    _app.config.from_mapping(config)
    return _app


with open(os.path.join(
        os.path.dirname(__file__),
        'config.json'
)) as cfg_file:
    cfg = json.load(cfg_file)
application = app_factory(cfg, None)


@application.route('/')
def main():
    return application.render_template('home.html', title="Movie Recommender -- Search")


@application.route('/search')
def search():
    query = flask.request.args.get('search-query')
    results = application.search(query)
    return application.render_template('search.html', "Movie Recommender -- Results",
                                       request=query,
                                       results=results)


@application.route('/movies/<name>')
def movie(name: str):
    sheet: DataFrame = application.index.sheet
    if name in sheet.index:
        return application.render_template(
            'movie.html', name, tags=sheet.loc[name, :].tolist()
        )
    else:
        return flask.Response(status=404)


@application.route('/lucky')
def lucky():
    movie = random.choice(application.index.movie_list)
    return flask.redirect(f'/movies/{movie}')


@application.route('/all')
def show_all():
    return application.render_template(
        'all.html', 'All Movies',
        table=application.index.sheet
    )
