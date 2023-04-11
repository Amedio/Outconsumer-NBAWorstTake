import math
import os
import random

import openai
from dotenv import load_dotenv
from textwrap import wrap
import twitter


class ai:
    """Generates a prompt and a text summary from certain imput data"""

    def __init__(self, basic_prompts=[{"text": "", "weight": 1}]):
        """Constructor"""
        # Credenciales de la API de OpenAI
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # setup basic openai parameters
        self.model = 'gpt-3.5-turbo'
        self.max_tokens = 1000
        self.n = 1
        self.stop = None
        self.temperature = 0.7
        self.basic_prompts = basic_prompts
        self.max_tweet_size = 280
        self.tweet_split_size = 270  # so that we can add the tread message index (n/M)
        self.min_tweet_size = 90
        # Important: randomize prompts based on system time
        random.seed()

    @property
    def basic_prompt(self):
        """returns one of the basic prompts, at random (weighted)"""
        if len(self.basic_prompts) == 0:
            return ""
        return random.choices([x['text'] for x in self.basic_prompts],
                              [x['weight'] for x in self.basic_prompts],
                              k=1)[0]

    def split_into_tweets(self, text):
        text_size = twitter.twitter.tweet_size(text)
        if text_size > self.max_tweet_size:
            # cut the tweet in several ones of max length tweet_split_size, but more or less
            # balanced (so the last one is not super-short)
            num_tweets = math.ceil(text_size / self.tweet_split_size)
            width = min(self.tweet_split_size, (text_size + 6 * num_tweets) / num_tweets)
            text_list = wrap(text, width=width)
            num_tweets = len(text_list)
            tweets = [tweet + f" ({i}/{num_tweets})" for i, tweet in enumerate(text_list, 1)]
        else:
            tweets = [text]

        return tweets

    def generate_text_from_chat(self, custom_prompt, postfix=""):
        # combine static and dynamic parts of the prompt
        basic_prompt = self.basic_prompt
        full_prompt = basic_prompt + custom_prompt
        # call chatGPT
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{'role': 'user', 'content': full_prompt}],
            max_tokens=self.max_tokens,
            n=self.n,
            stop=self.stop,
            temperature=self.temperature,
        )

        # split in a thread, if needed
        text = response.choices[0].message.content.strip('"') + postfix
        if len(postfix) > 0 and text.startswith('@'):  # do not @ when quoting
            text = '.' + text
        tweets = self.split_into_tweets(text)

        return tweets
