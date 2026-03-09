from openai import OpenAI
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from collections import defaultdict
import tempfile
import asyncio
import io

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERSONALITY_PROMPT = os.getenv('PERSONALITY_PROMPT1')
OWNER_ID =int(os.getenv('OWNER_ID'))

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Discord bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Store message history (user_id : [messages] )
user_conversations = defaultdict(list)

# Audio Queue
audio_queue = defaultdict(asyncio.Queue)

# Function to generate response using OpenAI GPT 3.5 Turbo (Doesn't need aysnc / await )
def generate_ai_response(user_id, user_message, reply_context):

    user_conversations[user_id].append({
        "role": "user",
        "content": user_message + reply_context if reply_context else user_message,
    })

    print(reply_context)

    messages = [{
        "role": "system",
        "content": PERSONALITY_PROMPT
    }] + user_conversations[user_id]

    if len(user_conversations[user_id]) > 20:
        user_conversations[user_id] = user_conversations[user_id][-20:]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        # max_tokens=150,
    )
    
    assistant_reply = response.choices[0].message.content.strip()
    user_conversations[user_id].append({
        "role": "assistant",
        "content": assistant_reply
    })

    return assistant_reply

# Function to convert text to speach and play in voice channel
async def speak_text(message, text: str):

    vc = message.guild.voice_client

    # if not vc or not vc.is_connected():
    #     return await message.channel.send(
    #         "I am not connected to a voice channel. Use !join."
    #     )

    try:

        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
        )

        audio_bytes = response.read()
        audio_stream = io.BytesIO(audio_bytes)

        await audio_queue[message.guild.id].put(audio_stream)

        if not vc.is_playing():
            await play_next(message.guild)

    except Exception as e:
        print("TTS streaming error:", e)
        await message.channel.send("Audio playback failed.")


async def play_next(guild):

    vc = guild.voice_client
    queue = audio_queue[guild.id]

    if queue.empty():
        return

    stream = await queue.get()

    source = discord.FFmpegPCMAudio(
        stream,
        pipe=True
    )

    def after_playing(error):
        asyncio.run_coroutine_threadsafe(
            play_next(guild),
            bot.loop
        )

    vc.play(source, after=after_playing)


# Event: When bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is now running!")

# Event: Respond to messages
@bot.event
async def on_message(message):
    vc = message.guild.voice_client if message.guild else None
    if message.author == bot.user:
        return
    
    if not isinstance(message.channel, discord.DMChannel) and bot.user.mentioned_in(message):
        # Get replied-to message if exists
        replied_to = None
        if message.reference and message.reference.resolved:
            replied_to = message.reference.resolved
        elif message.reference:
            try:
                replied_to = await message.channel.fetch_message(message.reference.message_id)
            except Exception as e:
                print("Error fetching replied message:", e)


        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        print(user_message)
        async with message.channel.typing():
            try:
                reply_context = replied_to.content if replied_to else None
                response = generate_ai_response(message.author.id, user_message, reply_context)
                await message.channel.send(response)

                if vc and vc.is_connected():
                    await speak_text(message, response)
            except Exception as e:
                await message.channel.send("Something went wrong.")
                print("Error", e)

    await bot.process_commands(message)

# Event: Bot Error Handling
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in event {event}: {args} {kwargs}")

# Command: Bot Join Voice Channel
@bot.command()
async def join(ctx):
    print("Join command invoked")
    if ctx.voice_client:
        return await ctx.send("I am already connected to a voice channel!")
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect(reconnect=True)
        await ctx.send(f"Joined {channel}")
    else:
        await ctx.send("You are not connected to a voice channel.")

# Command: Bot Leave Voice Channel
@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        return await ctx.send("I am not connected to a voice channel!")
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not connected to any voice channel.")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
    