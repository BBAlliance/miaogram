from controllers.base import Args, onCommand, onMessage, Context
from pyrogram import Client
from pyrogram.types import Message

import aiohttp
import asyncio

toggler = {}
s = aiohttp.ClientSession()

def getToken(msg: Message) -> str:
    if msg and msg.chat and msg.from_user:
        return f"{msg.chat.id}:{msg.from_user.id}"
    return ""

@onMessage(minVer="1.0.0")
async def msgHandler(client: Client, msg: Message, ctx: Context):
    t = getToken(msg)
    if not t:
        return
    
    if t in toggler and toggler[t]:
        try:
            r = await s.get("https://zuan.shabi.workers.dev")
            if (r.status / 200) == 1:
                text = f'**{await r.text()}**'
                text = f'[@{msg.from_user.first_name}](tg://user?id={msg.from_user.id}) ' + text
                
                if msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_self:
                    await msg.reply_text(text)
                else:
                    await client.send_message(msg.chat.id, text, 'MD')
        except:
            pass

@onCommand("autodiss", minVer="1.0.0", help="autodiss: 回复一个人来开启自动骂人", version="1.0.0")
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    if msg.reply_to_message:
        t = getToken(msg.reply_to_message)
        if not t:
            await msg.edit("他不是个人！")
        elif t in toggler and toggler[t]:
            toggler[t] = False
            await msg.edit("自动嘴臭已关闭～")
        else:
            toggler[t] = True
            await msg.edit("自动嘴臭已开启～")
    else:
        await msg.edit("错误，请回复一则消息哦～")
    
    await asyncio.sleep(3)
    await msg.delete()
