import discord
from discord.ext import commands
from discord.ext import voice_recv
from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv
from collections import defaultdict
from discord import FFmpegPCMAudio

# Load env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERSONALITY_PROMPT = os.getenv("PERSONALITY_PROMPT")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # needed for voice receive

bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI(api_key=OPENAI_API_KEY)

user_conversations = defaultdict(list)

def generate_ai_response(user_id, user_message):
    user_conversations[user_id].append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": PERSONALITY_PROMPT}] + user_conversations[user_id]
    if len(user_conversations[user_id]) > 20:
        user_conversations[user_id] = user_conversations[user_id][-20:]
    response = client.chat.completions.create(model="gpt-4.1", messages=messages)
    assistant_reply = response.choices[0].message.content.strip()
    user_conversations[user_id].append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

async def speak_text(vc: discord.VoiceClient, text: str):
    resp = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(resp.read())
        f.flush()
        audio_src = FFmpegPCMAudio(f.name)

    if vc.is_playing():
        vc.stop()
    vc.play(audio_src, after=lambda e: os.remove(f.name))

# Audio sink class
class MySink(voice_recv.AudioSink):
    def __init__(self):
        super().__init__()
        self.buffers = {}

    def write(self, user: discord.User, data: voice_recv.VoiceData):
        if user.bot:
            return
        if user.id not in self.buffers:
            self.buffers[user.id] = open(f"user_{user.id}.pcm", "ab")
        self.buffers[user.id].write(data.pcm)

    def cleanup(self):
        for f in self.buffers.values():
            try:
                f.close()
            except:
                pass
        self.buffers.clear()

    def wants_opus(self) -> bool:
        # False = give me raw PCM frames (easier to feed into ffmpeg / Whisper)
        return False


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        sink = MySink()
        vc.listen(sink)
        await ctx.send(f"Joined {channel} and listening for speech.")
    else:
        await ctx.send("You’re not in a voice channel.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        # stop listening
        ctx.voice_client.stop_listening()
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def process_speech(ctx, user: discord.Member):
    pcm_path = f"user_{user.id}.pcm"
    if not os.path.exists(pcm_path):
        return await ctx.send(f"No audio recorded for {user.display_name}. Use join + speak first.")

    wav_path = f"user_{user.id}.wav"
    # Convert raw PCM to WAV with ffmpeg
    # This assumes default PCM format from sink; you might need to adjust sample rate etc.
    os.system(f"ffmpeg -f s16le -ar 48000 -ac 2 -i {pcm_path} {wav_path}")

    # Transcribe using Whisper
    with open(wav_path, "rb") as wf:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=wf)
    user_text = transcript.text

    await ctx.send(f"🗣 {user.display_name} said: {user_text}")

    # Get GPT reply
    reply = generate_ai_response(user.id, user_text)
    await ctx.send(reply)

    # Speak reply if bot is connected
    vc = ctx.guild.voice_client
    if vc:
        await speak_text(vc, reply)

    # Optional: clean up files
    os.remove(pcm_path)
    os.remove(wav_path)

@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user}")

bot.run(DISCORD_TOKEN)
