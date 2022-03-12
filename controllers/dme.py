from typing import List, Union
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.methods.messages.search_messages import get_chunk
import time
import asyncio

iterLimit = 2000

# 修改内置的方法使得返回的消息全部倒序
async def searchMessageReverse(
    client,
    chat_id: Union[int, str],
    query: str = "",
    offset: int = 0,
    filter: str = "empty",
    limit: int = 0,
    from_user: Union[int, str] = None):
    current = 0
    total = abs(limit) or (1 << 31) - 1
    limit = min(100, total)

    while True:
        messages = await get_chunk(
            client=client,
            chat_id=chat_id,
            query=query,
            filter=filter,
            offset=offset,
            limit=limit,
            from_user=from_user
        )

        if not messages:
            return
        offset += len(messages)

        for message in messages[::-1]:
            yield message

            current += 1
            if current >= total:
                return

@onCommand("!dme")
async def handler(args: Args, client: Client, message: Message):
    counter = 0
    limit = args.getInt(0)
    if limit > 1000 or limit <= 0:
        limit = 1000
    placeholder = "—— auto deletion ——"

    await message.edit("读取中...")
    wait_deletions: List[Message] = [message]
    id_maps = {}
    t = time.time()

    # 第一阶段，暴力扫描最近的消息，这些消息有可能无法搜索到
    async for msg in client.iter_history(message.chat.id, limit=iterLimit):
        if msg.from_user and msg.from_user.is_self and msg.message_id > 1:
            wait_deletions.append(msg)
            id_maps[msg.message_id] = True
            counter += 1
            if counter > limit:
                break
    
    # 第二阶段，对于老的消息直接扫描性能不好，还会触发限制，使用搜索功能来提速
    if counter <= limit:
        async for msg in searchMessageReverse(client, message.chat.id, from_user="me"):
            if msg.message_id > 1 and msg.from_user and msg.from_user.is_self and not msg.message_id in id_maps:
                wait_deletions.append(msg)
                counter += 1
                if counter > limit:
                    break
    
    # 第三阶段，批量修改并删除
    i = 0
    factor = 100
    while i < len(wait_deletions):
        for msg in wait_deletions[i: i+factor]:
            if msg.text and msg.text != placeholder:
                try:
                    await msg.edit(placeholder)
                    await asyncio.sleep(0.001)
                except:
                    pass
        await client.delete_messages(message.chat.id, [m.message_id for m in wait_deletions[i: i+factor]])
        i += factor
    
    t = int(time.time() - t)
    m = await message.reply(f"已成功删除 ({counter-1}/{limit}) 条消息 用时 {t} 秒 ~")

    await asyncio.sleep(3)
    await m.delete()
