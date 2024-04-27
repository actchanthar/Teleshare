import asyncio
import logging
import sys

from pyrogram.client import Client
from pyrogram.errors import ChannelInvalid, ChatAdminRequired
from pyrogram.sync import idle
from rich.logging import RichHandler
from rich.traceback import install

from bot.config import config
from bot.options import options
from bot.utilities.helpers import PyroHelper
from bot.utilities.http_server import HTTPServer
from bot.utilities.schedule_manager import schedule_manager

install(show_locals=True)

FORMAT = "%(message)s"
logging.basicConfig(level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

background_tasks = set()


async def main() -> None:
    http_server = HTTPServer(host="0.0.0.0", port=config.PORT)
    task = asyncio.create_task(http_server.run_server())
    background_tasks.add(task)

    bot_client = Client(
        "Zaws-File-Share",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workers=420,
        plugins={"root": "plugins"},
        max_message_cache_size=10,
    )

    # Load database settings
    await options.load_settings()
    await bot_client.start()
    # Bot setup
    try:
        channels_n_invite = await PyroHelper.get_channel_invites(client=bot_client, channels=config.FORCE_SUB_CHANNELS)
        bot_client.channels_n_invite = channels_n_invite  # type: ignore[reportAttributeAccessIssue]
    except (ChannelInvalid, ChatAdminRequired):
        sys.exit("Please add and give me permission in FORCE_SUB_CHANNELS and BACKUP_CHANNEL")
    await schedule_manager.start()
    await idle()
    task.add_done_callback(background_tasks.discard)
    await bot_client.stop()


asyncio.run(main())
