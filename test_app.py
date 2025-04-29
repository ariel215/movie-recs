from app import model
import os.path as osp

ROOT = osp.dirname(model.__file__)

def test_from_csv():
    csv_file = osp.join(ROOT, 'data', 'movie_tags.csv')
    index = model.Index.from_csv(
        csv_file
    )
    assert len(index.movies) == len(open(csv_file, encoding='utf8').readlines())