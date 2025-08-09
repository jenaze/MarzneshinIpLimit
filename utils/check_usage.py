"""
This module checks if a user (name and IP address)
appears more than two times in the ACTIVE_USERS list.
"""

import asyncio
from collections import Counter

from telegram_bot.send_message import send_logs
from utils.logs import logger
from utils.panel_api import disable_user
from utils.panel_api import all_user
from utils.read_config import read_config
from utils.read_config import detect_user
from utils.read_config import add_detected_user
from utils.read_config import delete_detected_user
from utils.read_config import get_detected_users
from utils.types import PanelType, UserType

ACTIVE_USERS: dict[str, UserType] | dict = {}


async def check_ip_used(panel_data: PanelType, owner: str = None) -> dict:
    """
    This function checks if a user (name and IP address)
    appears more than two times in the ACTIVE_USERS list.
    """

    all_users_log = {}
    allusers=[user.name for user in await all_user(panel_data)]
        
    for email in list(ACTIVE_USERS.keys()):
        data = ACTIVE_USERS[email]
        if owner and data.name not in allusers:
            continue
        ip_counts = Counter(data.ip)
        data.ip = list({ip for ip in data.ip if ip_counts[ip] > 2})
        all_users_log[email] = data.ip
        logger.info(data)
    total_ips = sum(len(ips) for ips in all_users_log.values())
    all_users_log = dict(
        sorted(
            all_users_log.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )
    )
    messages = [
        f"<code>{email}</code> with <code>{len(ips)}</code> active ip  \n- "
        + "\n- ".join(ips)
        for email, ips in all_users_log.items()
        if ips
    ]
    logger.info("Number of all active ips: %s", str(total_ips))
    messages.append(f"---------\nCount Of All Active IPs: <b>{total_ips}</b>")
    shorter_messages = [
        "\n".join(messages[i : i + 100]) for i in range(0, len(messages), 100)
    ]
    for message in shorter_messages:
        await send_logs(message)
    return all_users_log


async def check_users_usage(panel_data: PanelType):
    """
    checks the usage of active users
    """
    config_data = await read_config()
    owner = config_data.get("OWNER_USERNAME",None)
    if owner != None:
        all_users_log = await check_ip_used(panel_data, owner)
    else :
        all_users_log = await check_ip_used(panel_data)
    except_users = config_data.get("EXCEPT_USERS", [])
    special_limit = config_data.get("SPECIAL_LIMIT", {})
    limit_number = config_data["GENERAL_LIMIT"]
    out_of_limit_number = config_data["outOfLimitNumber"]
    detected_users= await get_detected_users()
    for user_name, user_ip in all_users_log.items():
        if user_name not in except_users:
            try:
                user_limit_number = int(next((u for u in special_limit if u[0] == user_name), None)[1])
            except:
                user_limit_number = limit_number
            detected_user=next((u for u in detected_users if u["user"] == user_name), None)
            if detected_user != None:
                ips = list(detected_user["ips"])
                if sum(1 for i in list(user_ip) if i in ips) > user_limit_number:
                    await detect_user(user_name, list(user_ip))
                    if int((detected_user["outOfLimitCount"]) + 1) >= out_of_limit_number:
                        message = (
                            f"User {user_name} has {str(len(set(user_ip)))}"
                            + f" active ips. {str(set(user_ip))}"
                        )
                        logger.warning(message)
                        await send_logs(str("<b>Warning: </b>" + message))
                        try:
                            await disable_user(panel_data, UserType(name=user_name, ip=[]))
                        except ValueError as error:
                            print(error)
                        await delete_detected_user(user_name)
                else:
                    await delete_detected_user(user_name)
            else:
                if len(set(user_ip)) > user_limit_number:
                    await add_detected_user(user_name,list(user_ip))
    ACTIVE_USERS.clear()
    all_users_log.clear()


async def run_check_users_usage(panel_data: PanelType) -> None:
    """run check_ip_used() function and then run check_users_usage()"""
    while True:
        await check_users_usage(panel_data)
        data = await read_config()
        await asyncio.sleep(int(data["CHECK_INTERVAL"]))
