import re
import discord
import os

TOKEN = os.environ["DISCORD_TOKEN"]

MONITORED_CHANNEL_IDS = {
    123456789012345678
}

BANNED_WORDS = [
    "mace",
    "jvc",
    "kill ace",
]

REPOST_CLEANED_MESSAGE = True
ONLY_MODERATE_BOTS = True


def compile_patterns(words):
    patterns = []
    for word in words:
        escaped = re.escape(word.strip())
        patterns.append(re.compile(rf"\b{escaped}\b", re.IGNORECASE))
    return patterns


PATTERNS = compile_patterns(BANNED_WORDS)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)


def censor_text(text):
    found = False
    cleaned = text

    for pattern in PATTERNS:
        if pattern.search(cleaned):
            found = True
            cleaned = pattern.sub("[censored]", cleaned)

    return found, cleaned


@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")


@client.event
async def on_message(message):
    if message.guild is None:
        return

    if message.channel.id not in MONITORED_CHANNEL_IDS:
        return

    if message.author.id == client.user.id:
        return

    if ONLY_MODERATE_BOTS:
        is_bot_or_webhook = message.author.bot or message.webhook_id is not None
        if not is_bot_or_webhook:
            return

    content = message.content or ""
    if not content:
        return

    matched, cleaned = censor_text(content)
    if not matched:
        return

    try:
        await message.delete()

        if REPOST_CLEANED_MESSAGE:
            name = getattr(message.author, "display_name", str(message.author))
            await message.channel.send(f"**{name}:** {cleaned}")

    except discord.Forbidden:
        print("Missing permission: Manage Messages")
    except discord.HTTPException as e:
        print(f"Failed to moderate message: {e}")


client.run(TOKEN)