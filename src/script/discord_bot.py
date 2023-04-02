# This example requires the 'message_content' intent.
from dotenv import load_dotenv

import discord

import stats

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!east'):
        await message.channel.send(stats.list_standings('east'))
    if message.content.startswith('!west'):
        await message.channel.send(stats.list_standings('west'))
    if message.content.startswith('!games'):
        await message.channel.send(stats.list_games())

load_dotenv()
client.run(os.getenv('DISCORD_KEY'))
