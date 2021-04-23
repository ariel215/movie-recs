from PyQt5 import QtWidgets
import sys
import os.path
import app.model
import json


class App(QtWidgets.QApplication):
    def __init__(self, argv):
        super(App, self).__init__(argv)

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("Semantic Movie Search")
        self.controller = Controller(self.window)
        self.window.setCentralWidget(self.controller)


class Controller(QtWidgets.QWidget):

    searchers = {
        'lda': app.model.LDASearcher,
        'tags': app.model.TagSearcher,
        'literal': app.model.LiteralSearcher,
    }

    def __init__(self, parent):
        super(Controller, self).__init__(parent)
        self.submit_button = SubmitButton(self, self)
        self.results_list = ResultsList()
        self.query_box = QueryBox(self, self)
        with open(os.path.join(os.path.dirname(__file__), 'config.json')) as cfgfd:
            self.config = json.load(cfgfd)
        searcher_cls = self.searchers[self.config['searcher']]
        self.searcher = searcher_cls(self.config)

        self.init_layout()

    def init_layout(self):

        query_layout = QtWidgets.QHBoxLayout()
        query_layout.addWidget(self.query_box)
        query_layout.addWidget(self.submit_button)

        search_layout = QtWidgets.QVBoxLayout(self)
        search_layout.addWidget(QtWidgets.QLabel("Semantic Movie Search Engine"))
        search_layout.addLayout(query_layout)
        search_layout.addWidget(self.results_list)
        self.setLayout(search_layout)

    def search(self, text):
        # TODO: IMPLEMENT
        print("Searching for {}".format(text))
        movie_names = self.searcher.search(text)
        self.results_list.clear()

        if len(movie_names):
            self.results_list.addItems(movie_names)
        else:
            self.results_list.addItem("No Results Found")


class ResultsList(QtWidgets.QListWidget):
    """
    If we want to add behavior to this widget, it might as well have its own class
    """
    pass


class QueryBox(QtWidgets.QLineEdit):

    def __init__(self, parent, controller):
        super(QueryBox, self).__init__(parent)
        self.controller = controller

        self.returnPressed.connect(self.controller.submit_button.search)


class SubmitButton(QtWidgets.QPushButton):
    def __init__(self, parent, controller):
        super(SubmitButton, self).__init__("Search", parent)
        self.controller = controller

        self.clicked.connect(self.search)

    def search(self):
        query_box = self.parent().query_box
        text = query_box.text()
        self.controller.search(text)


if __name__ == "__main__":

    app = App(sys.argv)
    app.window.show()
    app.exec_()
