from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

import aiohttp

proxy = {}
s = aiohttp.ClientSession()

@onCommand("!diss")
async def handler(args: Args, client: Client, msg: Message):
    m = await msg.edit_text('獲取中...')
    try:
        r = await s.get("https://zuan.shabi.workers.dev")
        if (r.status / 200) == 1:
            text = f'**{await r.text()}**'
            
            if msg.reply_to_message:
                text += f' [@{msg.reply_to_message.from_user.first_name}](tg://user?id={msg.reply_to_message.from_user.id})'
                await client.send_message(msg.chat.id, text, 'MD', reply_to_message_id=msg.reply_to_message.message_id)
            else:
                await client.send_message(msg.chat.id, text, 'MD')
    except:
        return await client.send_message(msg.chat.id, '失敗', 'MD', disable_web_page_preview=True)
      
      
    await m.delete()
