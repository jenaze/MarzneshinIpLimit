"""
This module contains functions to interact with the panel API
"""

import asyncio
import random
import sys
from ssl import SSLError

try:
    import httpx
except ImportError:
    print("Module 'httpx' is not installed use: 'pip install httpx' to install it")
    sys.exit()
from telegram_bot.send_message import send_logs

from utils.handel_dis_users import DISABLED_USERS, DisabledUsers
from utils.logs import logger
from utils.read_config import read_config
from utils.types import NodeType, PanelType, UserType

# Use tuple instead of list for schemes (better for performance)
SCHEMES = ("https", "http")


async def get_token(panel_data: PanelType) -> PanelType | ValueError:
    """
    Get access token from the panel API
    
    Args:
        panel_data (PanelType): PanelType object containing username, password, and domain

    Returns:
        PanelType: Panel data with access token

    Raises:
        ValueError: If failed to get token after 20 attempts
    """
    payload = {
        "username": panel_data.panel_username,
        "password": panel_data.panel_password,
    }
    
    for attempt in range(20):
        for scheme in SCHEMES:
            url = f"{scheme}://{panel_data.panel_domain}/api/admins/token"
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.post(url, data=payload, timeout=5)
                    response.raise_for_status()
                json_obj = response.json()
                panel_data.panel_token = json_obj["access_token"]
                return panel_data
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_logs(message)
                logger.error(message)
                continue
            except SSLError:
                continue
            except Exception as error:  # pylint: disable=broad-except
                if scheme == "https":
                    continue
                message = f"Unexpected error: {error}"
                await send_logs(message)
                logger.error(message)
                continue
        
        if attempt < 19:  # Only sleep if there's a next attempt
            await asyncio.sleep(random.randint(2, 5) * (attempt + 1))
    
    message = (
        "Failed to get token after 20 attempts. Make sure the panel is running "
        "and the username and password are correct."
    )
    await send_logs(message)
    logger.error(message)
    raise ValueError(message)


async def all_user(panel_data: PanelType) -> list[UserType] | ValueError:
    """
    Get the list of all users from the panel API

    Args:
        panel_data (PanelType): PanelType object containing panel information

    Returns:
        list[UserType]: List of users

    Raises:
        ValueError: If failed after 20 attempts
    """
    for attempt in range(20):
        get_panel_token = await get_token(panel_data)
        if isinstance(get_panel_token, ValueError):
            raise get_panel_token
        
        token = get_panel_token.panel_token
        headers = {"Authorization": f"Bearer {token}"}
        
        config_data = await read_config()
        owner = config_data.get("OWNER_USERNAME", None)
        
        for scheme in SCHEMES:
            # Determine URL based on owner existence
            if owner is not None:
                url = f"{scheme}://{panel_data.panel_domain}/api/users?owner_username={owner}"
            else:
                url = f"{scheme}://{panel_data.panel_domain}/api/users"
            
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                user_inform = response.json()
                return [UserType(name=user["username"]) for user in user_inform["items"]]
            except SSLError:
                continue
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_logs(message)
                logger.error(message)
                continue
            except Exception as error:  # pylint: disable=broad-except
                if scheme == "https":
                    continue
                message = f"Unexpected error: {error}"
                await send_logs(message)
                logger.error(message)
                continue
        
        if attempt < 19:
            await asyncio.sleep(random.randint(2, 5) * (attempt + 1))
    
    message = "Failed to get users after 20 attempts. Make sure the panel is running."
    await send_logs(message)
    logger.error(message)
    raise ValueError(message)


async def enable_all_user(panel_data: PanelType) -> None | ValueError:
    """
    Enable all users on the panel.

    Args:
        panel_data (PanelType): A PanelType object containing
        the username, password, and domain for the panel API.

    Returns:
        None

    Raises:
        ValueError: If the function fails to enable the users on both the HTTP
        and HTTPS endpoints.
    """
    get_panel_token = await get_token(panel_data)
    if isinstance(get_panel_token, ValueError):
        raise get_panel_token
    token = get_panel_token.panel_token
    headers = {
        "Authorization": f"Bearer {token}",
    }
    users = await all_user(panel_data)
    if isinstance(users, ValueError):
        raise users
    for username in users:
        for scheme in ["https","http"]:  # add this later: save what scheme is used
            url = f"{scheme}://{panel_data.panel_domain}/api/users/{username.name}/enable"
            status = {}
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.post(
                        url, json=status, headers=headers, timeout=5
                    )
                    response.raise_for_status()
                message = f"Enabled user: {username.name}"
                await send_logs(message)
                logger.info(message)
                break
            except SSLError:
                continue
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_logs(message)
                logger.error(message)
                continue
            except Exception as error:  # pylint: disable=broad-except
                if scheme == "https":
                    continue
                message = f"An unexpected error occurred: {error}"
                await send_logs(message)
                logger.error(message)
    logger.info("Enabled all users")


async def enable_selected_users(
    panel_data: PanelType, inactive_users: set[str]
) -> None | ValueError:
    """
    Enable selected users on the panel.

    Args:
        panel_data (PanelType): A PanelType object containing
        the username, password, and domain for the panel API.
        inactive_users (set[str]): A list of user str that are currently inactive.

    Returns:
        None

    Raises:
        ValueError: If the function fails to enable the users on both the HTTP
        and HTTPS endpoints.
    """
    for username in inactive_users:
        success = False
        for attempt in range(5):
            get_panel_token = await get_token(panel_data)
            if isinstance(get_panel_token, ValueError):
                raise get_panel_token
            token = get_panel_token.panel_token
            headers = {
                "Authorization": f"Bearer {token}",
            }
            status = {}
            for scheme in ["https","http"]:
                url = f"{scheme}://{panel_data.panel_domain}/api/users/{username}/enable"
                try:
                    async with httpx.AsyncClient(verify=False) as client:
                        response = await client.post(
                            url, json=status, headers=headers, timeout=5
                        )
                        response.raise_for_status()
                    message = f"Enabled user: {username}"
                    await send_logs(message)
                    config_data = await read_config()
                    webhook_url = config_data.get("WEBHOOK_URL", "")
                    if webhook_url:
                        async with httpx.AsyncClient() as client:
                            await client.post(webhook_url, json={"username": username, "status": "enabled"})
                    logger.info(message)
                    success = True
                    break
                except SSLError:
                    continue
                except httpx.HTTPStatusError:
                    if response.status_code == 409:
                        success = True
                        break
                    message = f"[{response.status_code}] {response.text}"
                    await send_logs(message)
                    logger.error(message)
                    continue
                except Exception as error:  # pylint: disable=broad-except
                    if scheme == "https":
                        continue
                    message = f"An unexpected error occurred: {error}"
                    await send_logs(message)
                    logger.error(message)
                    continue
            if success:
                break
            await asyncio.sleep(random.randint(2, 5) * attempt)
        if not success:
            message = (
                f"Failed enable user: {username} after 20 attempts. Make sure the panel is running "
                + "and the username and password are correct."
            )
            await send_logs(message)
            logger.error(message)
            raise ValueError(message)
    logger.info("Enabled selected users")


async def disable_user(panel_data: PanelType, username: UserType) -> None | ValueError:
    """
    Disable a user on the panel.

    Args:
        panel_data (PanelType): A PanelType object containing
        the username, password, and domain for the panel API.
        username (user): The username of the user to disable.

    Returns:
        None

    Raises:
        ValueError: If the function fails to disable the user on both the HTTP
        and HTTPS endpoints.
    """
        # فقط پیام ارسال می‌شود، کاربر غیرفعال نمی‌شود
    message = f"🚫 کاربر محدود شده شناسایی شد: {username.name} (فقط اطلاع‌رسانی - بدون غیرفعال‌سازی)"
    
    # ارسال پیام به تلگرام
    await send_logs(message, on_ban=True)
    
    # چاپ در کنسول
    print(message)
    logger.info(message)
    
    return None

async def disable_user2(panel_data: PanelType, username: UserType) -> None | ValueError:
    """
    Disable a user on the panel.

    Args:
        panel_data (PanelType): A PanelType object containing
        the username, password, and domain for the panel API.
        username (user): The username of the user to disable.

    Returns:
        None

    Raises:
        ValueError: If the function fails to disable the user on both the HTTP
        and HTTPS endpoints.
    """

    for attempt in range(20):
        get_panel_token = await get_token(panel_data)
        if isinstance(get_panel_token, ValueError):
            raise get_panel_token
        token = get_panel_token.panel_token
        headers = {
            "Authorization": f"Bearer {token}",
        }
        status = {}
        for scheme in ["https","http"]:
            url = f"{scheme}://{panel_data.panel_domain}/api/users/{username.name}/disable"
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.post(
                        url, json=status, headers=headers, timeout=5
                    )
                    response.raise_for_status()
                message = f"Disabled user: {username.name}"
                await send_logs(message,on_ban=True)
                config_data = await read_config()
                webhook_url = config_data.get("WEBHOOK_URL", "")
                if webhook_url:
                    async with httpx.AsyncClient() as client:
                        await client.post(webhook_url, json={"username": username.name, "status": "disabled"})

                logger.info(message)
                dis_obj = DisabledUsers()
                await dis_obj.add_user(username.name)
                return None
            except SSLError:
                continue
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_logs(message)
                logger.error(message)
                continue
            except Exception as error:  # pylint: disable=broad-except
                if scheme == "https":
                    continue
                message = f"An unexpected error occurred: {error}"
                await send_logs(message)
                logger.error(message)
                continue
        await asyncio.sleep(random.randint(2, 5) * attempt)
    message = (
        f"Failed disable user: {username.name} after 20 attempts. Make sure the panel is running "
        + "and the username and password are correct."
    )
    await send_logs(message)
    logger.error(message)
    raise ValueError(message)

async def get_nodes(panel_data: PanelType) -> list[NodeType] | ValueError:
    """
    Get the IDs of all nodes from the panel API.

    Args:
        panel_data (PanelType): A PanelType object containing
        the username, password, and domain for the panel API.

    Returns:
        list[NodeType]: The list of IDs and other information of all nodes.

    Raises:
        ValueError: If the function fails to get the nodes from both the HTTP
        and HTTPS endpoints.
    """
    for attempt in range(20):
        get_panel_token = await get_token(panel_data)
        if isinstance(get_panel_token, ValueError):
            raise get_panel_token
        token = get_panel_token.panel_token
        headers = {
            "Authorization": f"Bearer {token}",
        }
        all_nodes = []
        for scheme in ["https","http"]:
            url = f"{scheme}://{panel_data.panel_domain}/api/nodes"
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                user_inform = response.json()
                for node in user_inform["items"]:
                    all_nodes.append(
                        NodeType(
                            node_id=node["id"],
                            node_name=node["name"],
                            node_ip=node["address"],
                            status=node["status"],
                            message=node["message"],
                        )
                    )
                return all_nodes
            except SSLError:
                continue
            except httpx.HTTPStatusError:
                message = f"[{response.status_code}] {response.text}"
                await send_logs(message)
                logger.error(message)
                continue
            except Exception as error:  # pylint: disable=broad-except
                if scheme == "https":
                    continue
                message = f"An unexpected error occurred: {error}"
                await send_logs(message)
                logger.error(message)
                continue
        await asyncio.sleep(random.randint(2, 5) * attempt)
    message = (
        "Failed to get nodes after 20 attempts. make sure the panel is running "
        + "and the username and password are correct."
    )
    await send_logs(message)
    logger.error(message)
    raise ValueError(message)


async def enable_dis_user(panel_data: PanelType):
    """
    Enable disabled users every 'TIME_TO_ACTIVE_USERS' seconds.
    """
    dis_obj = DisabledUsers()
    while True:
        data = await read_config()
        await asyncio.sleep(int(data["TIME_TO_ACTIVE_USERS"]))
        if DISABLED_USERS:
            await enable_selected_users(panel_data, DISABLED_USERS)
            await dis_obj.read_and_clear_users()
