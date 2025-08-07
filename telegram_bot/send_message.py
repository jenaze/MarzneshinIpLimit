"""
Send logs to telegram bot.
"""
from utils.read_config import read_config
from telegram_bot.main import application
from telegram_bot.utils import check_admin


async def send_logs(msg, on_ban=False):
    """Send logs to all admins."""
    config_data = await read_config()
    telegram_message_mode = config_data.get("TELEGRAM_MESSAGE_MODE", "always")

    if telegram_message_mode == "silent":
        return
    if telegram_message_mode == "on_ban" and not on_ban:
        return

    admins = await check_admin()
    retries = 2
    if admins:
        for admin in admins:
            for _ in range(retries):
                try:
                    await application.bot.sendMessage(
                        chat_id=admin, text=msg, parse_mode="HTML"
                    )
                    break
                except Exception as e:  # pylint: disable=broad-except
                    print(f"Failed to send message to admin {admin}: {e}")
    else:
        print("No admins found.")
