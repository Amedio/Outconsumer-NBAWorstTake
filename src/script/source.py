import sys

import sources.as_news
import sources.kingsleague_twitter
import sources.marca_news
import sources.nba_stats
import sources.sport_news


class source:
    """An abstract representation of a source used to generate a prompt"""
    @staticmethod
    def get_source_factory(method):
        if method == "marca":
            return sources.marca_news.marca_news()
        elif method == "as":
            return sources.as_news.as_news()
        elif method == "sport":
            return sources.sport_news.sport_news()
        elif method == "twitter":
            return sources.kingsleague_twitter.kingsleague_twitter()
        elif method == "nba_api":
            return sources.nba_stats.nba_stats()
        return None
        
    @staticmethod
    def read_sources(method):
        """
        returns a list of source objects with at least an id with available
        information sources
        """
        factory = source.get_source_factory(method)
        if factory is None:
            return []
        return factory.get_sources()

    def __init__(self, id, method, date=None, sent=False, prompt=None, tweets=None):
        """Constructor"""
        self.id = id
        self.method = method
        self.date = date
        self.sent = sent
        self.prompt = prompt
        self.tweets = tweets

    def __repr__(self):
        """return the string representation of the source"""
        return str(self.id)

    def __iter__(self):
        """yield all attribute values, useful for generating a tuple with it"""
        yield self.id
        yield self.method
        yield self.date
        yield self.sent
        yield self.prompt
        yield self.tweets

    def get_prompt(self):
        """returns a generated text prompt for the current source"""
        factory = source.get_source_factory(self.method)
        if factory is None:
            return None
        return factory.generate_prompt(self)
