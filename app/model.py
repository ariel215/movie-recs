from dataclasses import dataclass
import enum
import heapq
import os
import csv
from typing import Dict, Iterable, List, Self, Set, Tuple
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
try: 
    stops = set(stopwords.words('english'))
except LookupError:
    import nltk
    nltk.download('stopwords')
    stops = set(stopwords.words('english'))

@dataclass
class Movie:
    id_: int
    name: str
    tags: Set["Tag"]

    def __hash__(self) -> int:
        return hash((self.id_, self.name))
    
    def __str__(self):
        tags_str = ', '.join(tag.value for tag in self.tags)
        return f"Movie(id={self.id_}, name='{self.name}', tags={tags_str})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Tag:
    id_: int
    value: str
    movies: Set[Movie]

    def __hash__(self) -> int:
        return hash((self.id_, self.value))
    
    def __str__(self):
        movies_str = ', '.join(movie.name for movie in self.movies)
        return f"Tag(id={self.id_}, value='{self.value}', movies={movies_str})"
    
    def __repr__(self):
        return self.__str__()

class ResultField(enum.Enum):
    NAME = 0
    TAGS = 1


@dataclass
class SearchResult:
    field: ResultField
    movie: Movie
    words: List[str]


_stemmer = PorterStemmer()


@dataclass
class Index: 
    movies: Dict[str, Movie]
    tags: Dict[str, Tag]


    def add_movie(self, movie_name: str, movie_id: int, tags: List[str], tag_id: int):

        if tags:
            self.movies[movie_name.lower()] = movie = Movie(movie_id, movie_name, set())
            movie_id += 1
            
            for t in (t.strip() for t in tags):
                if not t:
                    continue

                tag_words = [word.strip().lower() for word in t.split()]
                if len(tag_words) > 1:
                    tag_words.append(t)
                tag_words = list({word for word in tag_words if word not in stops})

                for word in tag_words:
                    tag = self.tags.get(word)
                    if not tag:
                        self.tags[word.lower()] = tag = Tag(tag_id, word, set())
                        tag_id += 1

                    stemmed = _stemmer.stem(word)
                    if stemmed not in self.tags:
                        self.tags[stemmed] = tag
                    
                    tag.movies.add(movie)
                movie.tags.add(self.tags[t.lower()]) # Only add the original tag to the movie's tags
        return (movie_id, tag_id)

    @classmethod
    def from_lists(cls, movie_tags: List[List[str]]):
        """
        Create an Index from a list of movie tags.
        The first element of each sublist is the movie name, and the rest are tags.
        """
        movie_id = 0
        tag_id = 0
        index = cls({},{})
        for lst in movie_tags: 
            movie, *tags = lst
            (movie_id, tag_id) = index.add_movie(movie, movie_id, tags,tag_id)
        return index

    @classmethod
    def from_csv(cls, path: os.PathLike, sep: str=',') -> Self:
        with open(path, 'rt', encoding='utf8') as contents:
            movie_id = 0
            tag_id = 0
            reader = csv.reader(contents, delimiter=sep, quotechar='"')
            index = cls({},{})
            for row in reader:
                name, *tags = row
                movie_id, tag_id = index.add_movie(name, movie_id, tags, tag_id)
            return index
    


    def search(self, query:str) -> List[SearchResult]:
        """
        Search for movies in the index based on a query string.

        Movies are ranked based on the following criteria:

        1. The entire query is an exact match for the movie name:
           return that movie
        2. The entire query is an exact for one or more of the movie's tags:
           If the query matches a tag exactly, return the movies matching that tag
           Otherwise, treat each word in the query as its own tag (except for stop words)
           and return the set of movies with all those tags
        3. The entire query is a partial match for the movie name

        If none of these produce a non-empty result set, check if:
        4. The query is a misspelling of a movie name or tag

        Otherwise:
        5. Return the set of movies that contain one or more tags, ranked by how many tags they contain
        6. The query is semantically similar to either the set of tags or the movie name
        

        Movies are returned in alphabetical order
        """
        query = query.lower()

        # 1: Exact match for movie name
        if title := self.movies.get(query):
            return [SearchResult(ResultField.NAME,title,title.name.split())]
        
        # 2: Exact match for single tag (1 or more words)
        if matching_tag := self.tags.get(query):
            return [SearchResult(ResultField.TAGS, movie,[matching_tag.value])
                     for movie in  sorted(matching_tag.movies, key = lambda m: m.name)]

        unique_words = set(word.strip().lower() for word in query.split() if word.strip() and word.lower() not in stops)

        # 3: Exact match for each tag in query (splitting on whitespace)
        if matches_all_tags := self.matching_all_tags(unique_words):
            return matches_all_tags
        
        # 4: Partial match for movie name
        if partial_names := sorted(
            (SearchResult(ResultField.NAME, movie, query.split()) for (name, movie) in self.movies.items() 
            if query in name),
            key=lambda result: result.movie.name
        ):
            return partial_names

        # 5: Partial match for tags
        if partial_tags := self.matching_any_tags(unique_words):
            return partial_tags

        return []        
    
    def matching_all_tags(self, words: Iterable[str]) -> List[SearchResult]:
        """
        Find movies that match all tags in the given list of words.
        Returns a list of SearchResult objects for movies that match all tags.
        """
        if not words:
            return []

        unique_words = words if isinstance(words, set) else set(words) 

        matching_movies = set()
        for word in unique_words:
            if tag := self.tags.get(word):
                matching_movies.update(tag.movies)

        results = []
        for movie in matching_movies:
            tag_values = {tag.value for tag in movie.tags}
            if tag_values.issuperset(unique_words):
                results.append(SearchResult(ResultField.TAGS, movie, list(unique_words)))

        return sorted(results, key=lambda result: result.movie.name,)

    def matching_any_tags(self, words: Iterable[str]) -> List[SearchResult]:
        """
        Find movies that match any tag in the given list of words.
        Returns a list of SearchResult objects for movies that match any tag.
        """
        if not words:
            return []

        unique_words = words if isinstance(words, set) else set(words)

        matching_movies = set()
        for word in unique_words:
            if tag := self.tags.get(word):
                matching_movies.update(tag.movies)

        results = []
        for movie in matching_movies:
            tag_values = {tag.value for tag in movie.tags}
            intersection = unique_words & tag_values
            if intersection:
                results.append(SearchResult(ResultField.TAGS, movie, list(intersection)))
        
        return sorted(results, key=lambda result: len(result.words), reverse=True) 

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    index = Index.from_csv(os.path.join(here,'data/movie_tags.csv'))

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Search movie tags index")
    parser.add_argument('query', type=str, help="Query string to search for")
    args = parser.parse_args()
    results = index.search(args.query)
    print("Search results:")
    for result in results:
        print(f"Movie: {result.movie.name}")