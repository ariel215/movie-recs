from app.model import LDASearcher, TagSearcher, LiteralSearcher

def test_lda():
    cfg = {'model': 'ebert.lda'}
    searcher = LDASearcher(cfg)
    names = searcher.search("aliens")
    print(names[:5])


def test_tags():
    cfg = {'tags': 'movie_tags.csv'}
    searcher = TagSearcher(cfg)
    names = searcher.search("80s horror")
    print(names[:5])


def test_literals():
    cfg  = {'tags': 'movie_tags.csv'}
    searcher = LiteralSearcher(cfg)
    names = searcher.search("Sports")

    print(names)


if __name__ == "__main__":

    #test_lda()
    #test_tags()
    test_literals()
