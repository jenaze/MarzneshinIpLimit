"""Run the telegram bot."""

import asyncio
from utils.logs import logger

from telegram_bot.main import application


async def run_telegram_bot():
    """Run the telegram bot."""
    retry_delay = 5
    max_retry_delay = 300  # حداکثر 5 دقیقه تاخیر / Max 5 minutes delay
    
    while True:
        try:
            logger.info("Starting Telegram bot...")
            async with application:
                await application.start()
                await application.updater.start_polling()
                logger.info("Telegram bot started successfully!")
                retry_delay = 5  # ریست تاخیر پس از اتصال موفق / Reset delay after successful connection
                while True:
                    await asyncio.sleep(40)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Telegram bot error: {e}")
            logger.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            # افزایش تدریجی تاخیر / Gradually increase delay
            retry_delay = min(retry_delay * 2, max_retry_delay)
