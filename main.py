import os
import re
import discord

TOKEN = os.environ["DISCORD_TOKEN"]

# Replace this with the channel ID where Verixen sends messages
MONITORED_CHANNEL_IDS = {
    1456771536609349807
}

# Optional: replace this with Verixen's bot user ID if you want to target only that bot
# To use it, put the real ID number there. If you leave it as None, it will target any bot/webhook message in the channel.
TARGET_BOT_ID = None

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)


def contains_bang_word(text: str) -> bool:
    return bool(re.search(r'!\S+', text))


def extract_message_text(message: discord.Message) -> str:
    parts = []

    if message.content:
        parts.append(message.content)

    for embed in message.embeds:
        if embed.title:
            parts.append(embed.title)
        if embed.description:
            parts.append(embed.description)
        for field in embed.fields:
            if field.name:
                parts.append(field.name)
            if field.value:
                parts.append(field.value)

    return "\n".join(parts).strip()


@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")


@client.event
async def on_message(message: discord.Message):
    try:
        # Ignore DMs
        if message.guild is None:
            return

        # Only watch the channel(s) you choose
        if message.channel.id not in MONITORED_CHANNEL_IDS:
            return

        # Ignore this bot's own messages
        if message.author.id == client.user.id:
            return

        # Only moderate bot/webhook messages
        if not (message.author.bot or message.webhook_id is not None):
            return

        # If you set TARGET_BOT_ID, only moderate that one bot
        if TARGET_BOT_ID is not None and message.author.id != TARGET_BOT_ID:
            return

        # Read normal text + embed text
        text_to_scan = extract_message_text(message)

        # If there is no readable text, skip
        if not text_to_scan:
            return

        # Delete message if it contains any word starting with !
        if not contains_bang_word(text_to_scan):
            return

        await message.delete()
        print(f"Deleted message from {message.author} in #{message.channel}")

    except discord.Forbidden:
        print("Missing permission: Manage Messages")
    except discord.HTTPException as e:
        print(f"Failed to delete message: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


client.run(TOKEN)
