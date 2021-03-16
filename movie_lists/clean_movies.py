import os

def clean_movies(fname):
    with open(fname,'r') as in_:
        movie_list = [x for x in in_ if x[0].isnumeric()]
    movie_list = [x.partition(' ')[-1] for x in movie_list]
    names = [x.partition('(')[0].strip() for x in movie_list]
    dates = [x.rpartition(')')[0].rpartition('(')[-1] for x in movie_list]
    with open(os.path.splitext(fname)[0]+'.csv','w') as output:
        for (n,d) in zip(names,dates):
            output.write('{}\t{}\n'.format(n,d))

if __name__ == "__main__":
    for fname in ("horror_movies","romance_movies","thriller_movies"):
        clean_movies(fname+".txt")