import os
import sys
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import discord
from discord.ext import commands
from dotenv import load_dotenv

import lenh
import ai
from prefix_system import prefix_system

# Read .env file
load_dotenv()

if sys.version_info < (3, 12, 0) or sys.version_info >= (3, 13, 0):
    detected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    raise RuntimeError(
        "Yukki bot requires Python 3.12.x (tested on 3.12.10). "
        f"Detected Python {detected}. Please install Python 3.12.10."
    )

if sys.version_info[:3] != (3, 12, 10):
    detected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    try:
        print(
            "⚠️  Yukki bot is validated on Python 3.12.10. "
            f"Current interpreter is {detected}. Consider switching to 3.12.10 for voice stability"
        )
    except UnicodeEncodeError:
        print(
            "[WARNING] Yukki bot is validated on Python 3.12.10. "
            f"Current interpreter is {detected}. Consider switching to 3.12.10 for voice stability"
        )

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env file")
if not OPENROUTER_KEY:
    print("⚠️ Warning: Missing OPENROUTER_API_KEY in .env file — AI Takopi will not work")

def get_prefix(bot, message):
    """Get custom prefix for the guild, default is !"""
    if message.guild:
        return prefix_system.get_prefix(str(message.guild.id))
    return "!"  # Default prefix for DMs

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

@bot.event
async def on_ready():
    # Set streaming status
    activity = discord.Streaming(
        name=f"rn, {len(bot.guilds)} servers",
        url="https://twitch.tv/dorothyismyluv"
    )
    await bot.change_presence(activity=activity)
    
    print(f"✅ Logged in as {bot.user}")
    print(f"🌸 Active in {len(bot.guilds)} servers")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

def main():
    lenh.setup(bot)
    bot.run(TOKEN)

if __name__ == "__main__":
    main()