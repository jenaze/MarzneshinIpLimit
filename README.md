<p align="center">
    <a href="#">
        <img src="https://img.shields.io/github/license/jenaze/MarzneshinIpLimit?style=flat-square" />
    </a>
    <a href="https://t.me/jenaze" target="_blank">
        <img src="https://img.shields.io/badge/telegram-group-blue?style=flat-square&logo=telegram" />
    </a>
    <a href="#">
        <img src="https://img.shields.io/github/stars/jenaze/MarzneshinIpLimit?style=social" />
    </a>
</p>

<center>

# MarzneshinIpLimit

<b>Limiting the number of active users with IP for [Marzneshin](https://github.com/marzneshin/marzneshin)</b><sub> (with xray logs)</sub><br>
**An Enhanced Fork of [v2iplimit](https://github.com/houshmand-2005/v2iplimit) by Houshmand**<br>
**Featuring Stronger Algorithms and Resolved Issues from v2iplimit**<br>
**Supports IPv4, IPv6, and Marz-node**<br>
<sub>(Tested on Ubuntu 22.04 & 24.04, Fedora 39 & 40)</sub>

</center>

<hr>

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Telegram Bot Commands](#telegram-bot-commands)
- [API Documentation](#api-documentation)
- [Manual Configuration](#manual-configuration)
---
## Overview

This project is an advanced version of v2iplimit, forked and improved to address the limitations and challenges of the original code. Key enhancements include:

- Stronger, more efficient algorithms.
- Fixes for inaccuracies in IP counting.
- Expanded functionality and compatibility.
---
## Installation

Install command:

```bash
sudo bash -c "$(curl -sL https://github.com/jenaze/MarzneshinIpLimit/raw/main/script.sh)" @ install
```

1. Enter your bot token
   Create a telegram bot with [bot father](https://t.me/BotFather) and enter it
   
3. Enter admin chat id
   Get admin chat id with [My Id Bot](https://t.me/myidbot) and enter it
   
5. Enter your panel address, user and password
   First enter your panel address without http or https like: sub.example.com:443
   Second enter your panel username
   Third enter your panel password

Adjust other settings from the telegram bot

For manage the app use `marzneshiniplimit` command:

- `up`              Start services 
- `down`            Stop services
- `restart`         Restart services
- `status`          Show status
- `logs`            Show logs
- `token`           Set telegram bot token
- `admins`          Set telegram admins
- `install`         Install MarzneshinIpLimit
- `update`          Update latest version
- `uninstall`       Uninstall MarzneshinIpLimit
- `install-script`  Install MarzneshinIpLimit script

## Telegram Bot Commands

MarzneshinIpLimit can be controlled via a Telegram bot. Here are the available commands:

- **`/start`**: Start the bot.
- **`/create_config`**: Configure panel information (username, password, etc.).
- **`/set_special_limit`**: Set a specific IP limit for each user (e.g., test_user limit: 5 IPs).
- **`/show_special_limit`**: Show the list of special IP limits.
- **`/add_admin`**: Give access to another chat ID and create a new admin for the bot.
- **`/admins_list`**: Show the list of active bot admins.
- **`/remove_admin`**: Remove an admin's access to the bot.
- **`/country_code`**: Set your country. Only IPs related to that country are counted (to increase accuracy).
- **`/set_except_user`**: Add a user to the exception list.
- **`/remove_except_user`**: Remove a user from the exception list.
- **`/show_except_users`**: Show the list of users in the exception list.
- **`/set_general_limit_number`**: Set the general limit number. If a user is not in the special limit list, this is their limit number.
- **`/set_check_interval`**: Set the check interval time.
- **`/set_time_to_active_users`**: Set the time to active users.
- **`/backup`**: Send the `config.json` file.


---

## API Documentation

MarzneshinIpLimit includes APIs to manage special limits programmatically. These APIs allow you to add, update, or delete special limits while ensuring security with JWT tokens.

### Login API

This endpoint is used to authenticate and obtain a JWT token.

**Endpoint:**

```http
POST http://127.0.0.1:6284/login
```

**Request Body:**

```json
{
    "username": "admin",
    "password": "password"
}
```

**Response Example:**

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczNDY5ODIyMH0.1XZfDarMnNX-J0wCIVFY3bvL1ZKvNV_eEuUuCDl_Noo",
    "type": "bearer"
}
```

### Update Special Limit API

This endpoint updates or adds a special IP limit for a specific user.

**Endpoint:**

```http
POST http://127.0.0.1:6284/update_special_limit
```

**Headers:**

```http
Authorization: Bearer <JWT Token>
Content-Type: application/json
```

**Request Body:**

```json
{
    "user": "test",
    "limit": 2
}
```

### Note:

- This API ensures that special limits are securely updated or added with the help of JWT authentication.
- The server runs on port **6284**.
- Proper authorization is required to access these endpoints. Ensure your token is valid and not expired.

---

## Manual Configuration

### config.json
```json
{
    "GENERAL_LIMIT":1,
    "BOT_TOKEN": "BotToken",
    "ADMINS":[112234455],
    "EXCEPT_USERS": [
        ["user"]
    ],
    "PANEL_USERNAME": "username",
    "PANEL_PASSWORD": "pass",
    "PANEL_DOMAIN": "address:port", //Without http or https
    "SECRET_KEY": "supersecretkey", //Change to a strong string like: @j#@#kjlk! 
    "API_USERNAME": "username",
    "API_PASSWORD": "password",
    "CHECK_INTERVAL": 30,
    "TIME_TO_ACTIVE_USERS": 2400,
    "SPECIAL_LIMIT": [
        ["user", 1]
    ],
    "outOfLimitNumber": 3, //How often to check user IPs
    "IP_LOCATION":"IR" //IP filter
}
```
---

