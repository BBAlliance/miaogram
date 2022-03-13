import time
import json
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

@onCommand("!re")
async def handler(args: Args, client: Client, message: Message):
    count = args.getInt(0)
    if count > 10 or count <= 0:
        count = 1
    
    await message.delete()

    reply = message.reply_to_message
    if reply:
        canForward = not reply.has_protected_content and not reply.chat.has_protected_content
        for _ in range(count):
            if canForward:
                await reply.forward(message.chat.id)
            else:
                await reply.copy(message.chat.id)
