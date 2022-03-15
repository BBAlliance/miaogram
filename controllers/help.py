from .base import Args, onCommand, modules
from pyrogram import Client
from pyrogram.types import Message
from utils.config import Config

@onCommand("help", help="help: 查看菜单")
async def handler(_: Args, client: Client, message: Message):
    output = "🌞 当前启用的指令有:\n"
    for k in modules:
        m = modules[k]
        if m.help:
            line = Config["prefix"] + m.help
            output += "\n`" + line.replace("`", "'") + "`"
    await message.edit(f"{output}", 'md')
