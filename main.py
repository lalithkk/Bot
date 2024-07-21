import discord
import os
import requests
import json
import random
from replit import db
from dotenv import load_dotenv
from alive import alive

load_dotenv()  # Load environment variables from .env file

sad_words = [
    "sad", "depressed", "unhappy", "angry", "miserable", "depressing",
    "depression"
]
starter_encouragements = [
    "cheer up!", "hang in there, everything will be okay",
    "you are a great person!", "you are an amazing person! don't worry",
    "you are a good person!", "don't worry, everything will be fine!",
    "don't be sad, everything's gonna be fine!"
]

if "responding" not in db.keys():
    db["responding"] = True


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = list(db["encouragements"])
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]


def delete_encouragement(index):
    if "encouragements" in db.keys():
        encouragements = list(db["encouragements"])
        if len(encouragements) > index:
            del encouragements[index]
            db["encouragements"] = encouragements


intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('hello'):
        await message.channel.send('Hello!')

    if msg.startswith('inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if db["responding"]:
        options = starter_encouragements
        if "encouragements" in db.keys():
            options = options + list(db["encouragements"])

    if any(word in msg for word in sad_words):
        await message.channel.send(random.choice(options))

    if msg.startswith("new"):
        encouraging_message = msg.split("new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")

    if msg.startswith("del"):
        encouragements = []
        if "encouragements" in db.keys():
            index = int(msg.split("del", 1)[1])
            delete_encouragement(index)
            encouragements = list(db["encouragements"])
        await message.channel.send(encouragements)

    if msg.startswith("list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = list(db["encouragements"])
        await message.channel.send(encouragements)

    if msg.startswith("responding"):
        value = msg.split("responding ", 1)[1]

    if value.lower() == "true":
        db["responding"] = True
        await message.channel.send("Responding is on.")
    else:
        db["responding"] = False
        await message.channel.send("Responding is off.")


token = os.getenv("TOKEN")

if not token:
    raise ValueError("No TOKEN found in environment variables.")

alive()
client.run(token)
