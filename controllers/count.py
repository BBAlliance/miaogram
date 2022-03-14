from typing import List, Union
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.methods.messages.search_messages import get_chunk
import time
import asyncio

@onCommand("!count")
async def handler(args: Args, client: Client, message: Message):
    await message.edit("读取中...")
    t = time.time()

    target = "me"
    targetName = "我"
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
        targetName = "TA"
    
    count = await client.search_messages_count(message.chat.id, from_user=target)

    t = int((time.time() - t) * 1000)
    await message.edit(f"在当前群组中搜索到 {targetName} 发送的 {count} 条信息 用时 {t} 毫秒 ~")

    await asyncio.sleep(10)
    await message.delete()
