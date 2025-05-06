from dataclasses import dataclass
import os
import csv
import pdb
from typing import Dict, List, Self, Set, Tuple
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

    def __hash__(self):
        return hash((self.id_, self.name))

@dataclass
class Tag:
    id_: int
    value: str
    movies: Set[Movie]

    def __hash__(self):
        return hash((self.id_, self.value))

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
                tag_words = {word for word in tag_words if word not in stops}

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
    


    def search(self, query:str) -> List[Movie]:
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

        title = self.movies.get(query)
        if title:
            return [title]
            
        if match := self.tags.get(query):
            return sorted(match.movies, key = lambda m: m.name)

        result = set()
        tag_matches = set()
        tag_near_matches = set()
        words = query.split()
        for word in words:
            tag_match = self.tags.get(word) 
            if tag_match:
                tag_matches.update(tag_match.movies)
            stem = _stemmer.stem(word)
            stem_match = self.tags.get(stem)
            if stem_match:
                tag_near_matches.update(stem_match.movies)
        if result:
            result &= (tag_matches | tag_near_matches)
        else:
            result = tag_matches | tag_near_matches
        
        if result:
            return sorted(result, key=lambda movie: movie.name)
        
        partial_names = sorted(
            name for name in self.movies 
            if query in name
        )

        if partial_names:
            return [self.movies[name] for name in partial_names]
        
        words = set(words)
        results: List[Tuple[Movie,int]] = []
        for movie in self.movies.values():
            tag_values = {tag.value for tag in movie.tags}
            intersection = len(tag_values & words)
            if intersection:
                results.append((movie,intersection))
        
        return [m for m, i in sorted(results, key = lambda m_i: m_i[1])]
        
        