from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from utils.utils import bash

@onCommand("!sysinfo")
async def handler(_: Args, client: Client, message: Message):
    output = (await bash("vendors/neofetch.sh --stdout")).replace("`", "'")
    await message.edit(f"`{output}`", 'MD')
