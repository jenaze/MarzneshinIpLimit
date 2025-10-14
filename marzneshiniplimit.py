"""
marzneshiniplimit.py is the
main file that run other files and functions to run the program.
"""

import argparse
import asyncio

from run_telegram import run_telegram_bot
from utils.check_usage import run_check_users_usage
from utils.get_logs import (
    TASKS,
    check_and_add_new_nodes,
    create_node_task,
    handle_cancel,
    handle_cancel_all,
)
from utils.handel_dis_users import DisabledUsers
from utils.logs import logger
from utils.panel_api import (
    enable_dis_user,
    enable_selected_users,
    get_nodes,
)
from utils.read_config import read_config
from utils.types import PanelType

VERSION = "1.0.6"

parser = argparse.ArgumentParser(description="Help message")
parser.add_argument("--version", action="version", version=VERSION)
args = parser.parse_args()

TASKS = {}
dis_obj = DisabledUsers()
config_file = None

async def reload_config():
    """Reload config.json every 5 seconds."""
    global config_file
    while True:
        try:
            config_file = await read_config(check_required_elements=False)
            logger.info("Config reloaded.")
        except ValueError as error:
            logger.error(f"Error loading config: {error}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        await asyncio.sleep(5)


async def main():
    """Main function to run the code."""
    global config_file
    print("Telegram Bot running...")
    asyncio.create_task(run_telegram_bot())  # Start Telegram bot in a separate task
    await asyncio.sleep(2)
    
    # Load initial config
    config_file = await read_config(check_required_elements=True)

    # Initialize panel data
    panel_data = PanelType(
        config_file["PANEL_USERNAME"],
        config_file["PANEL_PASSWORD"],
        config_file["PANEL_DOMAIN"],
    )

    # Start periodic config reload
    asyncio.create_task(reload_config())

    # Enable disabled users initially
    dis_users = await dis_obj.read_and_clear_users()
    await enable_selected_users(panel_data, dis_users)

    # Fetch and process nodes
    await get_nodes(panel_data)

    async with asyncio.TaskGroup() as tg:
        nodes_list = await get_nodes(panel_data)
        if nodes_list and not isinstance(nodes_list, ValueError):
            print("Start Create Nodes Task Test: ")
            # خواندن لیست سرورهای مشخص شده از config
            servers = config_file.get("SERVERS", [])
            for node in nodes_list:
                if node.status == "healthy":
                    # فقط سرورهای مشخص شده را چک کن
                    if not servers or node.node_name in servers:
                        logger.info(f"Starting to check server: {node.node_name} (ID: {node.node_id})")
                        print(f"✓ Starting to check server: {node.node_name}")
                        await create_node_task(panel_data, tg, node)
                        await asyncio.sleep(4)
                    else:
                        logger.info(f"Server {node.node_name} is not in SERVERS list, skipping")
                        print(f"✗ Server {node.node_name} is not in the list")
        print("Start 'check_and_add_new_nodes' Task Test: ")
        tg.create_task(
            check_and_add_new_nodes(panel_data, tg),
            name="add_new_nodes",
        )
        print("Start 'handle_cancel' Task Test: ")
        tg.create_task(
            handle_cancel(panel_data, TASKS),
            name="cancel_disable_nodes",
        )
        tg.create_task(
            handle_cancel_all(TASKS, panel_data),
            name="cancel_all",
        )
        tg.create_task(
            enable_dis_user(panel_data),
            name="enable_dis_user",
        )

        # Run usage checking
        while True:
            await run_check_users_usage(panel_data)
            await asyncio.sleep(60)  # Main loop execution interval


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as er:  # Handle unexpected errors
        logger.error(f"Unexpected error: {er}")
