import os

import tweepy
from dotenv import load_dotenv
from pprint import pprint


class twitter:
    def __init__(self):
        load_dotenv()
        # Credenciales de la API de Twitter
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_KEY_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

    def authenticate(self):
        # Autenticación de Twitter
        self.client = tweepy.Client(consumer_key=self.api_key,
                                    consumer_secret=self.api_secret,
                                    access_token=self.access_token,
                                    access_token_secret=self.access_token_secret)

    def send(self, tweet, reply_to=None):
        """Publicar un tweet en Twitter"""
        response = self.client.create_tweet(text=tweet, in_reply_to_tweet_id=reply_to)
        pprint(response)
        return response

    def create_thread(self, tweets):
        """
        Crear un hilo con tantos tweets como textos se enviens en la lista de entrada.
        Devolver la respuesta del primer tweet publicado.
        """
        previous_tweet = None
        first_response = None
        for tweet in tweets:
            response = self.send(tweet, reply_to=previous_tweet)
            if first_response is None:
                first_response = response
            previous_tweet = response.data['id']
        return first_response
