from recommender import view
import sys


if __name__ == "__main__":
    app = view.App(sys.argv)
    app.window.show()
    sys.exit(app.exec_())
