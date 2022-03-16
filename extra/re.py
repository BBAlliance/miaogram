import time
import json
from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

@onCommand("re", minVer="1.0.0", help="re: 回复一则消息来复读")
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
                if message.reply_to_top_message_id and message.reply_to_top_message_id != reply.message_id:
                    await reply.copy(message.chat.id, reply_to_message_id=message.reply_to_top_message_id)
                else:
                    await reply.copy(message.chat.id)
