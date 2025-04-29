from dataclasses import dataclass
import os
from typing import Dict, List, Self, Set
from nltk.stem import PorterStemmer

@dataclass
class Movie:
    id_: int
    name: str
    tags: Set["Tag"]

@dataclass
class Tag:
    id_: int
    value: str
    movies: Set[Movie]

_stemmer = PorterStemmer()

@dataclass
class Index: 
    movies: Dict[str, Movie]
    tags: Dict[str, Tag]


    def add_movie(self, movie_name: str, movie_id: int, tags: List[str], tag_id: int):
        if tags:
            self.movies[movie_name] = movie = Movie(movie_id, movie_name, {})
            movie_id += 1
            
            for t in tags:
                tag_words = set(t.split())
                if len(tag_words) > 1:
                    tag_words.add(t)

                for word in tag_words:
                    tag = self.tags.get(word)
                    if not tag:
                        self.tags[word] = tag = Tag(tag_id, word, set())
                        tag_id += 1

                    stemmed = _stemmer.stem(word)
                    if stemmed not in self.tags:
                        self.tags[stemmed] = tag
                    
                    movie.tags.add(tag)
                    tag.movies.add(movie)

        return (movie_id, tag_id)


    @classmethod
    def from_csv(cls, csv: os.path.Pathlike, sep: str=',') -> Self:
        with open(csv) as contents:
            movie_id = 0
            tag_id = 0
            index = cls({},{})
            for line in contents:
                name, *tag_line = line.lower().split(sep)
                movie_id, tag_id = index.add_movie(name, movie_id, tag_line, tag_id)
        return cls(index.movies,index.tags)
    

    def search(self, query:str) -> List[Movie]:
        result = []
        title = self.movies.get(query)
        if title:
            result.append(title)
        
        tag_matches = []
        tag_near_matches = []
        words = query.split()
        for word in words:
            tag_match = self.tags.get(word) 
            if tag_match:
                tag_matches.append(tag_match)
            stem = _stemmer.stem(word)
            stem_match = self.tags.get(stem)
            if stem_match:
                tag_near_matches.append(stem_match)
        
        result.extend(tag_matches)
        result.extend(tag_near_matches)
        return result
        
