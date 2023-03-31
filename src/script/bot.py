import os
import tweepy
import openai
from dotenv import load_dotenv

import today_games_prompt

load_dotenv()

# Credenciales de la API de Twitter
consumer_key = 'TU_CONSUMER_KEY'
consumer_secret = 'TU_CONSUMER_SECRET'
access_token = 'TU_ACCESS_TOKEN'
access_token_secret = 'TU_ACCESS_TOKEN_SECRET'

# Autenticación de Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Crear objeto API de Twitter
api = tweepy.API(auth)

# Credenciales de la API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Generar el resumen del partido utilizando GPT-3
prompt = today_games_prompt.request_prompt()

print(prompt)
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7,
)

summary = response.choices[0].text

print(summary)

# Publicar el resumen del partido en Twitter
# api.update_status(summary)
