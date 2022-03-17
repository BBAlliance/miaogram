from .base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
from utils.utils import bash

@onCommand("sysinfo", minVer="1.0.0", help="sysinfo: 查看系统信息")
async def handler(_: Args, client: Client, message: Message, ctx: Context):
    output = (await bash("vendors/neofetch.sh --stdout")).replace("`", "'")
    await message.edit(f"`{output}`", 'MD')
