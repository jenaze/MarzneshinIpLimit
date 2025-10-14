import asyncio
from telegram.ext import ApplicationBuilder
from utils.read_config import read_config

data = asyncio.run(read_config())
try:
    bot_token = data["BOT_TOKEN"]
except KeyError as exc:
    raise ValueError("BOT_TOKEN is missing in the config file.") from exc

# سازنده برنامه با تنظیمات اتصال بهبود یافته
# Application builder with improved connection settings
app_builder = ApplicationBuilder().token(bot_token)

# پیکربندی پروکسی در صورت وجود در فایل تنظیمات
# Configure proxy if available in config file
if "PROXY_URL" in data and data["PROXY_URL"]:
    app_builder = app_builder.proxy_url(data["PROXY_URL"])
    
# افزایش تایم اوت برای اتصال بهتر
# Increase timeout for better connection
app_builder = app_builder.connect_timeout(30.0).read_timeout(30.0)

application = app_builder.build()
