from openai import OpenAI
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERSONALITY_PROMPT = os.getenv('PERSONALITY_PROMPT')

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Discord bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# Function to generate response using OpenAI GPT 3.5 Turbo (Doesn't need aysnc / await )
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


# Event: When bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is now running!")

# Event: Respond to messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if not isinstance(message.channel, discord.DMChannel) and bot.user.mentioned_in(message):
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        async with message.channel.typing():
            try:
                response = generate_ai_response(user_message)
                await message.channel.send(response)
            except Exception as e:
                await message.channel.send("Something went wrong.")
                print("Error", e)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
    