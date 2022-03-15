from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

import aiohttp

proxy = {}
s = aiohttp.ClientSession()

@onCommand("diss", help="autodiss: 回复一个人来骂 TA")
async def handler(args: Args, client: Client, msg: Message):
    m = await msg.edit_text('獲取中...')
    try:
        r = await s.get("https://zuan.shabi.workers.dev")
        await m.delete()
        if (r.status / 200) == 1:
            text = f'**{await r.text()}**'
            if msg.reply_to_message:
                text += f' [😘](tg://user?id={msg.reply_to_message.from_user.id})'
                await client.send_message(msg.chat.id, text, 'MD', reply_to_message_id=msg.reply_to_message.message_id)
            else:
                await client.send_message(msg.chat.id, text, 'MD')
                
    except:
        await client.send_message(msg.chat.id, '失敗', 'MD', disable_web_page_preview=True)
        return 
      
      
    
