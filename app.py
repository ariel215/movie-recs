import flask
import recommender.model
import os, json


class MyApp(flask.Flask):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(*args, **kwargs)
        self.searcher = None

    def search(self, string):
        return self.searcher.search(string)

    def set_searcher(self, srch):
        self.searcher = srch

    def render_template(self, template, title, **kwargs):
        return flask.render_template(template, styles=[
            'style.css'
        ], title=title,
         **kwargs)


def app_factory(config, searcher):
    if searcher is None:
        searcher = recommender.model.TagSearcher(config)
    _app = MyApp(__name__, instance_relative_config=True)
    _app.set_searcher(searcher)
    _app.config.from_mapping(config)
    return _app


with open(os.path.join(
        os.path.dirname(__file__),
        'config.json'
)) as cfg_file:
    cfg = json.load(cfg_file)
# searcher = recommender.model.TagSearcher(cfg)
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
