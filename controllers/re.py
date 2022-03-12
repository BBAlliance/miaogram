import time
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

@onCommand("!re")
async def handler(args: Args, client: Client, message: Message):
    count = args.getInt(0)
    if count > 10 or count <= 0:
        count = 1
    
    await message.delete()

    if message.reply_to_message:
        for _ in range(count):
            await message.reply_to_message.forward(message.chat.id)

