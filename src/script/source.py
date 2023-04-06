import sys

import sources.marca_news
import sources.nba_stats

class source:
    """An abstract representation of a source used to generate a prompt"""
    @staticmethod
    def read_sources(type):
        """
        returns a list of source objects with at least an id with available
        information sources
        """
        if type == "kings_league":
            mn = sources.marca_news.marca_news()
            return mn.get_sources()
        elif type == "nba":
            nba_api = sources.nba_stats.nba_stats()
            return nba_api.get_sources()
        else:
            return []

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
        if self.method == "marca":
            mn = sources.marca_news.marca_news()
            self.prompt = mn.generate_prompt(self)
        elif self.method == "nba_api":
            nba_api = sources.nba_stats.nba_stats()
            return nba_api.generate_prompt(self)
        return self.prompt
