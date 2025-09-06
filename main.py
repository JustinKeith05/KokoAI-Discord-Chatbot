from openai import OpenAI
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERSONALITY_PROMPT = os.getenv('PERSONALITY_PROMPT')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_response(user_message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": PERSONALITY_PROMPT},
            {"role": "user", "content": user_message}
        ],
        # max_tokens=150,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    while True:
        user_input = input ("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        ai_response = generate_ai_response(user_input)
        print("KokoAI: " + ai_response)

    