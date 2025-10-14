"""
Read config file and return data.
"""
# pylint: disable=global-statement

import json
import os
import sys
import time

CONFIG_DATA = None
LAST_READ_TIME = 0


async def read_config(
    check_required_elements=None,
) -> dict:
    """
    read and return data from a JSON file.
    """
    global CONFIG_DATA
    global LAST_READ_TIME
    config_file = "config.json"

    if not os.path.exists(config_file):
        print("Config file not found.")
        sys.exit()
    file_mod_time = os.path.getmtime(config_file)
    if CONFIG_DATA is None or file_mod_time > LAST_READ_TIME:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                CONFIG_DATA = json.load(f)
        except json.JSONDecodeError as error:
            print(
                "Error decoding the config.json file. Please check its syntax.", error
            )
            sys.exit()
        if "BOT_TOKEN" not in CONFIG_DATA:
            print("BOT_TOKEN is not set in the config.json file.")
            sys.exit()
        if "ADMINS" not in CONFIG_DATA:
            print("ADMINS is not set in the config.json file.")
            sys.exit()
        LAST_READ_TIME = time.time()
    if check_required_elements:
        required_elements = [
            "PANEL_DOMAIN",
            "PANEL_USERNAME",
            "PANEL_PASSWORD",
            "CHECK_INTERVAL",
            "TIME_TO_ACTIVE_USERS",
            "IP_LOCATION",
            "GENERAL_LIMIT",
        ]
        for element in required_elements:
            if element not in CONFIG_DATA:
                raise ValueError(
                    f"Missing required element '{element}' in the config file."
                )
    return CONFIG_DATA


async def read_detected_users_config(
    check_required_elements=None,
) -> dict:
    """
    Read and return data from detected_users.json file
    """
    config_file = "detected_users.json"

    if not os.path.exists(config_file):
        # Create file if it doesn't exist
        default_data = {"detectedUsers": []}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        return default_data
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as error:
        print(
            "Error decoding the detected_users.json file. Please check its syntax.", error
        )
        sys.exit()
    
    if check_required_elements:
        required_elements = ["detectedUsers"]
        for element in required_elements:
            if element not in data:
                raise ValueError(
                    f"Missing required element '{element}' in the detected_users file."
                )
    return data

async def detect_user(detectedUser: str, ips: list) -> str | None:
    """
    Add user to detected users list
    Creates config file if it doesn't exist
    """
    if os.path.exists("detected_users.json"):
        data = await read_d_json_file()
        users = data.get("detectedUsers", [])
        user_found = next((y for y in users if y["user"] == detectedUser), None)
        
        if user_found:
            # Update out of limit count
            user_found["outOfLimitCount"] = int(user_found.get("outOfLimitCount", 0)) + 1
            user_found["ips"] = ips
            with open("detected_users.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return detectedUser
        else:
            # Add new user
            users.append({"user": detectedUser, "ips": ips, "outOfLimitCount": 1})
            data["detectedUsers"] = users
            with open("detected_users.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return detectedUser
    else:
        # Create file with initial user
        data = {"detectedUsers": [{"user": detectedUser, "ips": ips, "outOfLimitCount": 1}]}
        with open("detected_users.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return detectedUser

async def add_detected_user(detectedUser: str, ips: list) -> str | None:
    """
    Add user to detected users list
    Creates config file if it doesn't exist
    """
    if os.path.exists("detected_users.json"):
        data = await read_d_json_file()
        users = data.get("detectedUsers", [])
        # Check if user exists
        if any(user["user"] == detectedUser for user in users):
            return detectedUser
        
        # Add new user
        users.append({"user": detectedUser, "ips": ips, "outOfLimitCount": 1})
        data["detectedUsers"] = users
        with open("detected_users.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return detectedUser
    else:
        # Create file with initial user
        data = {"detectedUsers": [{"user": detectedUser, "ips": ips, "outOfLimitCount": 1}]}
        with open("detected_users.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return detectedUser

async def delete_detected_user(detectedUser: str) -> str | None:
    """
    Remove user from detected users list
    """
    if not os.path.exists("detected_users.json"):
        return None
    
    data = await read_d_json_file()
    users = data.get("detectedUsers", [])
    user_to_remove = next((user for user in users if user["user"] == detectedUser), None)
    
    if user_to_remove:
        users.remove(user_to_remove)
        data["detectedUsers"] = users
        with open("detected_users.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return detectedUser
    return None


async def get_detected_users() -> list:
    """
    Get list of detected users
    """
    if os.path.exists("detected_users.json"):
        data = await read_d_json_file()
        return data.get("detectedUsers", [])
    
    # Create file if it doesn't exist
    data = {"detectedUsers": []}
    with open("detected_users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return []


async def read_d_json_file() -> dict:
    """
    Read and return contents of detected_users.json file

    Returns:
        Contents of detected_users.json file
    """
    with open("detected_users.json", "r", encoding="utf-8") as f:
        return json.load(f)
