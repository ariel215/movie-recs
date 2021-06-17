import flask
import recommender.model
import os, json


class MyApp(flask.Flask):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(*args, **kwargs)
        self.searcher = None

    def set_searcher(self, searcher):
        self.searcher = searcher

    def search(self, string):
        return self.searcher.search(string)

    def render_template(self, template, title, **kwargs):
        return flask.render_template(template, styles=[
            'style.css'
        ], title=title,
         **kwargs)


def app_factory(test_config=None):
    _app = MyApp(__name__, instance_relative_config=True)
    if test_config is None:
        with open(os.path.join(
            os.path.dirname(__file__),
            'config.json'
        )) as cfg_file:
            cfg = json.load(cfg_file)

    else:
        cfg = test_config
    _app.config.from_mapping(cfg)

    _app.set_searcher(recommender.model.TagSearcher(cfg))
    return _app


application = app_factory()


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
