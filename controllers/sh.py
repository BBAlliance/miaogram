from io import BytesIO
from .base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message

from getpass import getuser
from platform import node
from os import geteuid
from utils.utils import execute
from utils.config import VERSION

@onCommand("sh", help="sh <cmd>: 执行指令", version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    user = getuser()
    command = args.getAll()
    hostname = node()

    if not command:
        await msg.edit("请告诉我你想要执行的指令哦...")
        return

    usermark = "$"
    if geteuid() == 0:
        usermark = "#"
    headmark = f"`{user}@{hostname}{usermark}` `{command}`"
    await msg.edit(headmark, "md", disable_web_page_preview=True)

    try:
        result = await execute(command)
    except UnicodeDecodeError as e:
        result = str(e)

    if result:
        if len(result) >= 4096:
            await msg.delete()
            await client.send_document(msg.chat.id, BytesIO(bytes(result, encoding='utf-8')), caption=headmark, parse_mode='md', file_name='execution.log')
        else:
            result = result.replace("`", "'")
            await msg.edit(f"{headmark}\n\n`{result}`")
    else:
        await msg.edit(f"{headmark}\n\n`无结果返回`")
