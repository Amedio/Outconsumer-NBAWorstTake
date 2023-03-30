import tweepy
import openai
from nba_api.stats.endpoints import BoxScoreTraditionalV2

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
openai.api_key = 'TU_API_KEY_DE_OPENAI'

# Obtener datos del partido
game_id = 'GAME_ID_DEL_PARTIDO'
box_score = BoxScoreTraditionalV2(game_id=game_id)
data = box_score.get_normalized_dict()

# Analizar los datos del partido
home_team = data['basicGameData']['hTeam']['triCode']
home_score = data['basicGameData']['hTeam']['score']
away_team = data['basicGameData']['vTeam']['triCode']
away_score = data['basicGameData']['vTeam']['score']
top_scorer = data['stats'][0]['leadingScorer']['fullName']
top_scorer_pts = data['stats'][0]['leadingScorer']['points']

# Generar el resumen del partido utilizando GPT-3
prompt = f"Genera un resumen del partido entre {home_team} y {away_team} en el que {top_scorer} anotó {top_scorer_pts} puntos."
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7,
)

summary = response.choices[0].text

# Publicar el resumen del partido en Twitter
api.update_status(summary)
