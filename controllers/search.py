from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

import time

@onCommand("!sdme")
async def handler(args: Args, client: Client, message: Message):
    counter = 0
    limit = args.getInt(0)
    if limit > 1000 or limit <= 0:
        limit = 1000
    placeholder = "—— auto deletion ——"

    wait_deletions = []
    t = time.time()
    async for message in client.search_messages(message.chat.id, from_user="me"):
        if message.message_id > 1 and message.from_user and message.from_user.is_self:
            if message.text and message.text != placeholder:
                try:
                    await message.edit(placeholder)
                    time.sleep(0.001)
                except Exception:
                    pass
            wait_deletions.append(message.message_id)
            counter += 1

            if counter > limit:
                break
    
    # batch deletion
    i = 0
    factor = 100
    while i < len(wait_deletions):
        await client.delete_messages(message.chat.id, wait_deletions[i: i+factor])
        i += factor
    
    t = int(time.time() - t)
    m = await message.reply(f"已成功搜索并删除 {counter-1} 条消息 用时 {t} 秒 ~")

    time.sleep(3)
    await m.delete()