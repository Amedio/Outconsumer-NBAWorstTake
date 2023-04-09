import os
import signal
import sys
from time import sleep

from pprint import pprint
from ai import ai
import twitter
import prompts.kl_prompts
import prompts.nba_prompts
from db_tracking import db_tracking as tracking
from source import source


class bot:
    """Initializes and monitors sources to publish ai-generated tweets"""

    @staticmethod
    def signal_handler(signal, frame):
        print("Got SIGINT, requesting bot to stop.")
        sys.exit(0)


    def get_methods(self, type):
        """return the prompt sourcing methods for each bot type"""
        if type == 'kings_league':
            return ['marca', 'as', 'sport', 'relevo', 'twitter']
        elif type == 'nba':
            return ['nba_api']
        else:
            return []

    def __init__(self, type):
        """
        Setup the name/type of the bot, and the method used to get
        sources to create prompts
        """
        self.type = type
        if self.type == 'kings_league':
            self.twitter_account = "estaPasandoKL"
        elif self.type == 'nba':
            self.twitter_account = "TheNBAWorstTake"
        else:
            print("The bot type must be either kings_league or nba", file=sys.stderr)
            sys.exit(1)

        self.methods = self.get_methods(type)
        self.tracking = tracking(self.type)
        self.ai = None

    def get_sources(self):
        sources = []
        for method in self.methods:
            sources.extend(source.read_sources(method))
        return sources

    def initialize(self):
        # make sure basic infra is setup
        self.tracking.initialize()

        # set previous news and other sources as sent to
        # prevent duplicates
        sources = self.get_sources()
        for info in sources:
            self.tracking.track_source(info)
            self.tracking.set_sent(info)

        return 0

    def get_next_new_source(self):
        """
        Read the list of available sources and sent the next one
        that has not been already sent. If none are found or all have
        already been sent, return None
        """
        sources = self.get_sources()
        for s in sources:
            self.tracking.track_source(s)
            if not self.tracking.is_sent(s):
                return s
        return None

    def monitor(self):
        """
        Prepare twitter and OpenAI apis, and then monitor in an infinite loop
        for new sources to arrive, tweet them and go to sleep for some minutes
        """
        signal.signal(signal.SIGINT, bot.signal_handler)

        # setup twitter
        twitterer = twitter.twitter()

        # setup AI
        if self.type == 'nba':  # TODO: get basic_prompts and config from db
            basic_prompts = prompts.nba_prompts.basic_prompts
        else:
            basic_prompts = prompts.kl_prompts.basic_prompts
        self.ai = ai(basic_prompts=basic_prompts)

        while True:
            # check new sources
            info = self.get_next_new_source()
            if info is None:
                print(f"No new sources found")
            else:
                self.tracking.track_source(info)

                # generate prompt
                self.tracking.add_prompt(info, info.get_prompt())
                print(f"Using prompt: {info.prompt}")

                # call AI
                tweets = self.ai.generate_text_from_chat(custom_prompt=info.prompt)
                self.tracking.add_tweets(info, tweets)
                
                # tweet text
                print(f"Sending tweets: {tweets}")
                response = twitterer.create_thread(tweets)
                tweet_id = response.data['id']
                print(f"https://twitter.com/{self.twitter_account}/status/{tweet_id}")
                if len(response.errors) > 0:
                    print(response.errors)

                # track as done
                self.tracking.set_sent(info)

            # go to sleep
            print(f"Sleeping for {self.tracking.interval_time} seconds")
            sleep(self.tracking.interval_time)


def main():
    if len(sys.argv) <= 1:
        print("Running the bot requires a compulsory parameter: the type of bot (kings_league or nba)", file=sys.stderr)
        sys.exit(1)
    my_bot = bot(sys.argv[1])
    if len(sys.argv) >= 3 and sys.argv[2] == 'initialize':
        my_bot.initialize()
    else:
        my_bot.monitor()


if __name__ == "__main__":
    main()
