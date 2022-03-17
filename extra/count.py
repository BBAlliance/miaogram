from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
import time
import asyncio

@onCommand("count", minVer="1.0.0", help="count: 获取一个人发言数量")
async def handler(args: Args, client: Client, message: Message, ctx: Context):
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
