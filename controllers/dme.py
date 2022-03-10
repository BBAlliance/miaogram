from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

from utils import utils

import time

@onCommand("/!dme")
async def handler(args: Args, client: Client, message: Message):
    counter = 0
    limit = args.getInt(0)
    if limit > 1000 or limit <= 0:
        limit = 1000

    wait_deletions = []
    t = time.time()
    async for message in client.iter_history(message.chat.id):
        if message.from_user.is_self:
            if message.text:
                try:
                    await message.edit("—— auto deletion ——")
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
    m = await message.reply(f"已成功删除 {counter} 条消息 用时 {t} 秒 ~")

    time.sleep(3)
    await m.delete()
