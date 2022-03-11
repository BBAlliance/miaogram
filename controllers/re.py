import time
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

@onCommand("!re")
async def handler(_: Args, client: Client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.forward(message.chat.id)
    await message.delete()
