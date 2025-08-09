import asyncio
from telegram.ext import ApplicationBuilder
from utils.read_config import read_config

data = asyncio.run(read_config())
try:
    bot_token = data["BOT_TOKEN"]
except KeyError as exc:
    raise ValueError("BOT_TOKEN is missing in the config file.") from exc
application = ApplicationBuilder().token(bot_token).build()
