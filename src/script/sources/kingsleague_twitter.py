from datetime import datetime
from time import sleep
from urllib.request import urlopen, urlparse, Request
from urllib.error import URLError

from bs4 import BeautifulSoup
import snscrape.modules.twitter as sntwitter

import source
# import twitter


class kingsleague_twitter:
    """reads Kings-league related tweets and generates prompts with those"""

    twitter_account = 'KingsLeaguestat'
    num_tweets = 20
    method_name = 'twitter'

    def get_sources(self):
        """
        Get a list of kings leage related tweets with url as the id. Returns a
        list of non-duplicate source objects
        """
        # API is now under paywall ($100/month) :-(
        # twitterer = twitter.twitter()
        # tweet_ids = twitterer.get_tweets(self.twitter_account)
        tweet_ids = []
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(user=self.twitter_account).get_items()):
            if i > self.num_tweets:
                break
            tweet_ids.append(tweet.id)
        sources = []
        for id in tweet_ids:
            sources.append(source.source(id=id, method=self.method_name, date=datetime.now()))
        return sources

    def generate_prompt(self, s):
        """
        Given a news source s, with at least an id (tweet_id), return a string with a text prompt
        """
        #twitterer = twitter.twitter()
        #tweet_text = twitterer.get_tweet(s.id)
        for tweet in sntwitter.TwitterTweetScraper(tweetId=s.id).get_items():
            print(tweet)
            tweet_text = tweet.rawContent
            prompt = f"Reacciona al siguiente bombazo:\n\n{tweet_text}"
            return prompt
