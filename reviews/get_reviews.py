import os
import requests
import bs4
import pandas as pd
root = os.path.dirname(__file__)


def get_review_page(movie_name: str, movie_date: int):
    name_nospaces = movie_name.replace(" ", "-").lower()
    url = "http://rogerebert.com/reviews/{}-{}".format(name_nospaces,movie_date)
    webpage = requests.get(url)
    if webpage.status_code == 200:
        page = webpage.text
        return page


def get_review_txt(review_html):
    review_dom = bs4.BeautifulSoup(review_html)
    body = review_dom.find(itemprop="reviewBody")
    paragraphs = body.select('p')
    return '\n'.join(p.text for p in paragraphs if p.text != "Advertisement")


def download_review(name, year):
    if len(year) == 4:  # Valid release year
        print("Downloading {}".format(name))
        review_page = get_review_page(name, year)
        if review_page is not None:
            review_text = get_review_txt(review_page)
            name = name.lower().replace(' ', '_')
            with open(os.path.join(root, 'ebert', name + '_review.txt'), 'w') as review_file:
                review_file.write(review_text)


if __name__ == "__main__":
    for genre in ("horror_movies", "romance_movies", "thriller_movies"):
        lst_fname = os.path.join(os.path.dirname(root),"movie_lists", genre+".csv")
        movie_list = pd.read_csv(lst_fname,sep='\t')
        for _, (name, year) in movie_list.iterrows():
                download_review(name, year)
