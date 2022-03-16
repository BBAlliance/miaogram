from utils.config import reloadConfig
from .base import Args, onCommand, reloadPlugins
from pyrogram import Client
from pyrogram.types import Message

@onCommand("reload", minVer="1.0.0", help="reload: 重载配置和所有插件")
async def handler(_: Args, client: Client, message: Message):
    reloadConfig()
    success = reloadPlugins()
    success = "\n".join(success)
    await message.edit(f"🐛 重载这些插件成功啦:\n\n`{success}`", 'md')
